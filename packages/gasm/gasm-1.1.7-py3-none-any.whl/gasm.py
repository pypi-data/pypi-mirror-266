import sys
import os

def gasm():
    source = sys.argv[1]

    if (len(sys.argv) > 2):
        dest = sys.argv[2]
    else:
        # version command
        if sys.argv[1] in ['-v', '-V', '--version']:
            print('gasm by Michael Goppert\n1.1.7')
            exit(0)

        # deduce dest
        path = source.split('/')
        source_name = os.path.splitext(path[len(path) - 1])[0]
        dest = f'{source_name}.hex'

    in_data_block = False
    in_mis_block = False
    mis_block_ins = ''

    with open(dest, 'w') as o:
        with open(source) as i:
            lines = i.readlines()

            # resolve labels
            labels = {}
            resolved_lines = []
            offset_lines = 0
            ignored_lines = 0

            for line in lines:
                line = line.replace('\n', '')
                line_is_label = ((not '//' in line) and ':' in line) or (':' in line and '//' in line and (not line.strip().startswith('//')) and (line.strip().index(':') < line.index('//')))
                if line_is_label:
                    label, _ = line.split(':')
                    if label.lower() in ['end', 'sub', 'movl', 'movh', 'jz', 'jnz', 'js', 'jns', 'ld', 'st']:
                        print(f'INVALID LABEL ({label}) AT LINE {len(resolved_lines)}')
                        exit(1)
                    mem_word_loc = (len(resolved_lines) - ignored_lines + offset_lines) * 2
                    mem_loc = mem_word_loc + 1 if label.startswith('!mis_') else mem_word_loc
                    #if not label.startswith('!mis_'):
                    resolved_lines.append(f'// [PC: {hex(mem_loc)}] <{label}>:')
                    ignored_lines += 1
                    labels[label] =  mem_loc
                else:
                    if (not line) or line.strip().startswith('//') or line.strip().startswith('@'):
                        ignored_lines += 1
                    if '@END MISALIGNED' in line:
                        offset_lines += 1
                    resolved_lines.append(line)

            # update lines
            lines = resolved_lines

            # assemble
            for line_num, line in enumerate(lines):

                # comment
                comment = ''
                if line.strip().startswith('//'):
                    if '@BEGIN' in line or '@END' in line:
                        if 'DATA' in line:
                            in_data_block = not in_data_block
                        elif 'MISALIGNED' in line:
                            in_mis_block = not in_mis_block
                            mis_block_ins += 'ff'

                            # print result if no longer in block
                            if not in_mis_block:
                                for i in range(int(len(mis_block_ins) / 4)):
                                    o.write(f'{mis_block_ins[i * 4 : i * 4 + 4][::-1]}\n')
                                mis_block_ins = ''

                        o.write(f'{line}\n')
                    elif (line.startswith(' ' or line.startswith('\t'))):
                        o.write(f'        {line.strip()}\n')
                    else:
                        o.write(f'{line}\n')
                    continue
                elif '//' in line:
                    comment_index = line.index('//')
                    comment = line[comment_index:]
                    line = line[:comment_index].strip()

                # print data
                if in_data_block:
                    o.write(f'{line}\n')
                    continue

                # empty line
                if not line.strip():
                    if not in_mis_block:
                        o.write('\n')
                    continue

                # mem directive
                if line.startswith('@'):
                    o.write(f'{line}\n')
                    continue

                # remove extra symbols
                line = line.replace(',', '')

                # filter out whitespace
                u_comps = line.split(' ')
                comps = list(filter(lambda c: c != '' and c != ' ' and c != '\t', u_comps))

                # replace character literal
                for comp_num, comp in enumerate(comps):
                    if comp.startswith("'"):
                        lit = comp.split("'")[1]
                        comps[comp_num] = f'#{ord(lit)}'

                instr = comps[0]
                if len(comps) > 3:
                    rt = hex(int(comps[1][1:])).split('x')[-1]
                    ra = hex(int(comps[2][1:])).split('x')[-1]
                    rb = hex(int(comps[3][1:])).split('x')[-1]
                elif len(comps) > 1:
                    rt = hex(int(comps[1][1:])).split('x')[-1]
                    if instr in ['movl', 'movh'] and len(comps) > 2 and comps[2] in labels:
                        imm = hex(labels[comps[2]]).split('x')[-1]
                        imm = f'0{imm}' if len(imm) == 1 else imm
                    else:
                        ra = hex(int(comps[2][1:])).split('x')[-1] if instr not in ['movl', 'movh'] else '0'
                        imm = comps[2][3:] if comps[2][1:].startswith('0x') else hex(int(comps[2][1:])).split('x')[-1]
                        imm = f'0{imm}' if len(imm) == 1 else imm[:2]

                # convert to hex
                if instr == 'end':
                    if not in_mis_block:
                        o.write(f'ffff    {comment}\n')
                    else:
                        mis_block_ins += 'ffff'
                elif instr == 'sub':
                    if not in_mis_block:
                        o.write(f'0{ra}{rb}{rt}    {comment}\n')
                    else:
                        mis_block_ins += f'0{ra}{rb}{rt}'[::-1]
                elif instr == 'movl':
                    if not in_mis_block:
                        o.write(f'8{imm}{rt}    {comment}\n')
                    else:
                        mis_block_ins += f'8{imm}{rt}'[::-1]
                elif instr == 'movh':
                    if not in_mis_block:
                        o.write(f'9{imm}{rt}    {comment}\n')
                    else:
                        mis_block_ins += f'9{imm}{rt}'[::-1]
                elif instr == 'jz':
                    if not in_mis_block:
                        o.write(f'e{ra}0{rt}    {comment}\n')
                    else:
                        mis_block_ins += f'e{ra}0{rt}'[::-1]
                elif instr == 'jnz':
                    if not in_mis_block:
                        o.write(f'e{ra}1{rt}    {comment}\n')
                    else:
                        mis_block_ins += f'e{ra}1{rt}'[::-1]
                elif instr == 'js':
                    if not in_mis_block:
                        o.write(f'e{ra}2{rt}    {comment}\n')
                    else:
                        mis_block_ins += f'e{ra}2{rt}'[::-1]
                elif instr == 'jns':
                    if not in_mis_block:
                        o.write(f'e{ra}3{rt}    {comment}\n')
                    else:
                        mis_block_ins += f'e{ra}3{rt}'[::-1]
                elif instr == 'ld':
                    if not in_mis_block:
                        o.write(f'f{ra}0{rt}    {comment}\n')
                    else:
                        mis_block_ins += f'f{ra}0{rt}'[::-1]
                elif instr == 'st':
                    if not in_mis_block:
                        o.write(f'f{ra}1{rt}    {comment}\n')
                    else:
                        mis_block_ins += f'f{ra}1{rt}'[::-1]
                else:
                    print(f'INVALID ASM INSTRUCTION ({line}) AT LINE {line_num}')
                    exit(1)

if __name__ == '__main__':
    gasm()
