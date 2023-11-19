import lxml.etree as ET
#import xml.etree.ElementTree as ET
import argparse
import sys




#Function to manage the arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="interpretation of a IPPeCode in XML format")
    
    
    
    parser.add_argument("-i", "--input", metavar="input_file", type=argparse.FileType("r"), default=sys.stdin, help="Input file for values in instructions READSTR and READINT, if omitted use stdin.")
    
    parser.add_argument("program_file", metavar="program_file",  help="program file with XML representation of an IPPeCode source code")

    parser.add_argument("-o", "--output", metavar="output_file", type=argparse.FileType("w"), default=sys.stdout, help="Output file for values of instructions PRINT, if omitted use stdout")
    
    args = parser.parse_args()

    return args.input, args.program_file, args.output


#Function to get all the instructions and its arguments
#Also for checking if the file can not be opened
def parse_xml(file):
    
    
    try:
        tree = ET.parse(file)
    except ET.ParseError as e:
        sys.exit("20")
    except FileNotFoundError as e:
        sys.exit("20")
    root = tree.getroot()

    

    instructions = []

    #Each instruction is going to be stored as a dictionary (inst), that way 'instructions' will have a dictionary for each instruction
    for tac in root.iter('tac'):
        inst = {}
        inst['opcode'] = tac.get('opcode')
        #print(inst['opcode'])
        inst['order'] = tac.get('order')
        for elem in tac:
            inst[elem.tag] = {'type': elem.get('type'), 'value': elem.text}
        instructions.append(inst)

    #Just checking if the code was captured correctly
    """"
    for e in instructions:
        print(e)
    """

    return instructions

#Definition of all instructions, each instruction will be defined as a function 
def execute_instructions(instructions, input_file, output_file):

    def execute_MOV(inst, state):
        #print("Executing MOV")
        dst = inst['dst']['value']
        src = inst['src1']['value']
        
        if inst['src1']['type'] == 'integer':
            state['variables'][dst] = int(src)
        else:
            state['variables'][dst] = state['variables'].get(src, 0)
        
        #print(state)

    def execute_ADD(inst, state):
        #print("Executing ADD")
        dst = inst['dst']['value']
        src1 = inst['src1']['value']
        src2 = inst['src2']['value']
        if inst['src1']['type'] == 'integer':
            if inst['src2']['type'] == 'integer':
                state['variables'][dst] = int(src1) + int(src2)
            else:
                state['variables'][dst] = int(src1) + int(state['variables'].get(src2, 0))
        else:
            if inst['src2']['type'] == 'integer':
                state['variables'][dst] = int(state['variables'].get(src1, 0)) + int(src2)
            else:
                state['variables'][dst] = int(state['variables'].get(src1, 0)) + int(state['variables'].get(src2, 0))
        #print(state)

    def execute_SUB(inst, state):
        #print("Executing SUB")
        dst = inst['dst']['value']
        src1 = inst['src1']['value']
        src2 = inst['src2']['value']
        if inst['src1']['type'] == 'integer':
            if inst['src2']['type'] == 'integer':
                state['variables'][dst] = int(src1) - int(src2)
            else:
                state['variables'][dst] = int(src1) - int(state['variables'].get(src2, 0))
        else:
            if inst['src2']['type'] == 'integer':
                state['variables'][dst] = int(state['variables'].get(src1, 0)) - int(src2)
            else:
                state['variables'][dst] = int(state['variables'].get(src1, 0)) - int(state['variables'].get(src2, 0))
        #print(state)

    def execute_MUL(inst, state):
        #print("Executing MUL")
        dst = inst['dst']['value']
        src1 = inst['src1']['value']
        src2 = inst['src2']['value']
        if inst['src1']['type'] == 'integer':
            if inst['src2']['type'] == 'integer':
                state['variables'][dst] = int(src1) * int(src2)
            else:
                state['variables'][dst] = int(src1) * int(state['variables'].get(src2, 0))
        else:
            if inst['src2']['type'] == 'integer':
                state['variables'][dst] = int(state['variables'].get(src1, 0)) * int(src2)
            else:
                state['variables'][dst] = int(state['variables'].get(src1, 0)) * int(state['variables'].get(src2, 0))
        #print(state)

    def execute_DIV(inst, state):
        #print("Executing DIV")
        dst = inst['dst']['value']
        src1 = inst['src1']['value']
        src2 = inst['src2']['value']

        if inst['src2']['type'] == 'integer':
            divisor = int(src2)
        else:
            divisor = int(state['variables'].get(src2, 0))

        
        if divisor == 0:
            sys.exit("25")

        if inst['src1']['type'] == 'integer':
            state['variables'][dst] = int(src1) // divisor
        else:
            state['variables'][dst] = int(state['variables'].get(src1, 0)) // divisor
        #print(state)


    def execute_READINT(inst, state):
        #print("Executing READINT")
        dst = inst['dst']['value']
        try:
            value = int(input_file.readline().strip())
        except ValueError:
            sys.exit("26")
        state['variables'][dst] = value

    def execute_READSTR(inst, state):
        #print("Executing READSTR")
        dst = inst['dst']['value']
        value = input_file.readline().strip()
        state['variables'][dst] = value
    """"
    def execute_PRINT(inst, state):
        #print("Executing PRINT")
        src1 = inst['src1']['value']
        if inst['src1']['type'] == 'string':
            print(src1, file=output_file, end='', flush=True)
        else:
            print(state['variables'].get(src1, ''), file=output_file, end='', flush=True)
    """  
    def execute_PRINT(inst, state):
        #print("Executing PRINT")
        src1 = inst['src1']['value']
        if inst['src1']['type'] == 'string':
            output_file.write(src1 + '\n')
        else:
            output_file.write(str(state['variables'].get(src1, '')) + '\n')
        output_file.flush()

    #Labels will not do anything, we already have checked its semantic
    #They will be taken into account whenever we have a instruction that mentions it such as JUMP
    def execute_LABEL(inst, state):
        #print("going thorugh label")
        pass

    def execute_JUMP(inst, state):
        #print("Executing JUMP")
        label = inst['dst']['value']
        if label in state['labels']:
            state['pc'] = state['labels'][label] - 1
        else:
            sys.exit("23")

    def execute_JUMPIFEQ(inst, state):
        #print("Executing JUMPIFEQ")
        label = inst['dst']['value']
        src1 = inst['src1']['value']
        src2 = inst['src2']['value']
        
        if label in state['labels']:
            if inst['src1']['type'] == 'integer':   
                if inst['src2']['type'] == 'integer':
                    if int(src1) == int(src2):
                        state['pc'] = state['labels'][label] - 1
                    
                else:
                    if int(src1) == int(state['variables'].get(src2, 0)):
                        state['pc'] = state['labels'][label] - 1
            else:
                if inst['src2']['type'] == 'integer':
                    if int(state['variables'].get(src1, 0)) == int(src2):
                        state['pc'] = state['labels'][label] - 1
                else:
                    if int(state['variables'].get(src1, 0)) == int(state['variables'].get(src2, 0)):
                        state['pc'] = state['labels'][label] - 1
        else:
            sys.exit("23")
        
        #print(state)
        """"
        if state['variables'].get(src1, 0) == state['variables'].get(src2, 0):
            if label in state['labels']:
                state['pc'] = state['labels'][label] - 1
            else:
                sys.exit(23)
        """
    def execute_JUMPIFLT(inst, state):
        #print("Executing JUMPIFLT")
        label = inst['dst']['value']
        src1 = inst['src1']['value']
        src2 = inst['src2']['value']
        if label in state['labels']:
            if inst['src1']['type'] == 'integer':   
                if inst['src2']['type'] == 'integer':
                    if int(src1) < int(src2):
                        state['pc'] = state['labels'][label] - 1
                    
                else:
                    if int(src1) < int(state['variables'].get(src2, 0)):
                        state['pc'] = state['labels'][label] - 1
            else:
                if inst['src2']['type'] == 'integer':
                    if int(state['variables'].get(src1, 0)) < int(src2):
                        state['pc'] = state['labels'][label] - 1
                else:
                    if int(state['variables'].get(src1, 0)) < int(state['variables'].get(src2, 0)):
                        state['pc'] = state['labels'][label] - 1
        else:
            sys.exit("23")

    def execute_CALL(inst, state):
        #print("Executing CALL")
        label = inst['dst']['value']
        state['stack'].append(state['pc'])
        if label in state['labels']:
            state['pc'] = state['labels'][label] - 1
        else:
            sys.exit("23")

    def execute_RETURN(inst, state):
        #print("Executing RETURN")
        if not state['stack']:
            sys.exit("28")
        state['pc'] = state['stack'].pop()

    def execute_PUSH(inst, state):
        #print("Executing PUSH")
        src1 = inst['src1']['value']
        state['stack'].append(state['variables'].get(src1, 0))

    def execute_POP(inst, state):
        #print("Executing POP")
        if not state['stack']:
            sys.exit("28")
        dst = inst['dst']['value']
        state['variables'][dst] = state['stack'].pop()
    

    state = {'variables': {}, 'pc': 0, 'stack': [], 'labels': {}}
    num_instructions = len(instructions)

    # Process all the labels before anything else
    #In this scenario, if a label is repeated, the program exits with a semantic error
    for inst in instructions:
        if inst['opcode'] == 'LABEL':
            label = inst['dst']['value']
            if label in state['labels']:
                sys.exit("21")
            state['labels'][label] = int(inst['order'])

    
    # Ejecutar instrucciones
    while state['pc'] < num_instructions:
        inst = instructions[state['pc']]


        opcode = inst['opcode']
        
        if opcode == 'MOV':
            execute_MOV(inst, state)
        elif opcode == 'ADD':
            execute_ADD(inst, state)
        elif opcode == 'SUB':
            execute_SUB(inst, state)
        elif opcode == 'MUL':
            execute_MUL(inst, state)
        elif opcode == 'DIV':
            execute_DIV(inst, state)
        elif opcode == 'READSTR':
            execute_READSTR(inst, state)
        elif opcode == 'READINT':
            execute_READINT(inst, state)
        elif opcode == 'PRINT':
            execute_PRINT(inst, state)
        elif opcode == 'JUMP':
            execute_JUMP(inst, state)
        elif opcode == 'JUMPIFEQ':
            execute_JUMPIFEQ(inst, state)
        elif opcode == 'JUMPIFLT':
            execute_JUMPIFLT(inst, state)
        elif opcode == 'CALL':
            execute_CALL(inst, state)
        elif opcode == 'RETURN':
            execute_RETURN(inst, state)
        elif opcode == 'PUSH':
            execute_PUSH(inst, state)
        elif opcode == 'POP':
            execute_POP(inst, state)
        elif opcode == 'LABEL':
            execute_LABEL(inst, state)
        else:
            sys.exit("30")
        

        state['pc'] += 1
        
        
        
    """"
    for key in state:
        print(key, state[key])
    """

def main():

    input_file, program_file, output_file,  = parse_arguments()

    print(program_file)

        
    instructions = parse_xml(program_file)
    execute_instructions(instructions, input_file, output_file)

    

if __name__ == "__main__":
    main()

