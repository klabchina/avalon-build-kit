import os
import string
import click
import random
from datetime import datetime
from json import JSONEncoder

VOWELS = "aeioudmngjlefghisdfasdaswds"
CONSONANTS = "".join(set(string.ascii_lowercase) - set(VOWELS))
REPOSITORY_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
match_string1 = 'int y =arc4random()%100;'
match_string2 = 'int y = arc4random_uniform(100);'
match_string3 = '[KJPNotification application:application didReceiveLocalNotification:notification];'

function_used = ['denyDebuggerAssembly', 'amIJailbroken', 'amIRunInEmulator', 'amIReverseEngineered', 'amIDebugged']
to_obfsucator_function = ['denyDebugger', 'denySymbolHook' , 'denyMSHook', 'amIMSHookFunction', 'amIProxied', 'amIRuntimeHook', 'amITampered', 'amIJailbrokenWithFailMessage', 'denyDebuggerAssembly', 'amIJailbroken', 'amIRunInEmulator', 'amIReverseEngineered', 'amIDebugged']
IOSSecuritySuite = "IOSSecuritySuite"


def generate_word(length):
    word = ""
    random.seed(datetime.now())
    for i in range(length):
        if i % 2 == 0:
            word += random.choice(CONSONANTS)
        else:
            word += random.choice(VOWELS)
    one_word = random.choice(VOWELS).upper()
    return one_word + word


class FlatternFunctionInf:
    def __init__(self, name: string, split_num: int = 3, bcf_loop: int =2, sub_loop: int = 2):
        self.name = name
        self.split_num = split_num
        self.bcf_loop = bcf_loop
        self.sub_loop = sub_loop


class ObfsucaotrConfig:
    def __init__(self, fla: int = 1, bcf: int = 0, sub: int = 1):
        self.fla = fla
        self.bcf = bcf
        self.sub = sub
        self.obfuscation = []

    def addFunToFlattern(self, funInf: FlatternFunctionInf):
        self.obfuscation.append(funInf)


class ObfsucaotrConfigEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__




def create_flattern_funs_json(name_dic: dict, obfs_cfg_path: string)-> string:
    random_seed = generate_word(30)
    obfsucatorCnf = ObfsucaotrConfig()
    for key in name_dic.keys():
        if key in function_used:
            value = name_dic[key]
            obfsucatorCnf.addFunToFlattern(FlatternFunctionInf('l_'+value))
    random_function_name = 'l_abbac' + generate_word(30)
    obfsucatorCnf.addFunToFlattern(FlatternFunctionInf(random_function_name))
    obfsucatorCnf.addFunToFlattern(FlatternFunctionInf("set_pgdb"))
    obfsucatorCnf.addFunToFlattern(FlatternFunctionInf("set_pgdb_interface"))
    jsonStr = ObfsucaotrConfigEncoder().encode(obfsucatorCnf)
    with open(obfs_cfg_path, 'w') as outfile:
        outfile.writelines(jsonStr)
    return random_function_name

def create_unused_funs(num: int, length : int = 30)-> dict:
    random_unused_function_name = {}
    for  i in range(num):
        random_fun_name = 'l_abbac' + generate_word(length)
        if random_fun_name not in random_unused_function_name.keys():
            random_unused_function_name[random_fun_name] =  random_fun_name
    return random_unused_function_name


def generate_codes_h(targety_file_name: string, source_class_name: string):
    filename = source_class_name + '+' + targety_file_name+'.h'
    if os.path.exists(filename):
        os.remove(filename)
    insert_string = '''//
//  this h file is auto generate by
//  GeneralRandomFunction.py
//  do not modify it
//

'''
    with open(filename, 'w') as fd:
        insert_string += f'#import "{source_class_name}.h"\n\nNS_ASSUME_NONNULL_BEGIN\n'
        insert_string += f'@interface {source_class_name} ({targety_file_name})\n'
        insert_string += '''@end

NS_ASSUME_NONNULL_END'''
        fd.writelines(insert_string)



def generate_codes_mm(dic_names: dict, random_function_name: string,targety_file_name: string, source_class_name: string, random_unused_function_name: dict):
    filename = source_class_name + '+' + targety_file_name+'.mm'
    unused_function_name_list =  list(random_unused_function_name.keys())
    random_insert_order = random.randint(10, len(unused_function_name_list) - 1)
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'w') as fd:
        contents = []
        count = 1
        obfuscate_ios_security_suite = dic_names[IOSSecuritySuite]
        del dic_names[IOSSecuritySuite]
        insert_string = '''//
//  this mm file is auto generate by
//  GeneralRandomFunction.py
//  do not modify it
//

'''
        # initialize function define
        insert_string += f'#import "{source_class_name}+{targety_file_name}.h"\n'
        insert_string += '''#import <IOSUtilSuite/IOSUtilSuite-Swift.h>\n'''
        insert_string += f'@implementation {source_class_name} ({targety_file_name})\n'
        insert_string += """+ (void)initialize\n{\n"""
        insert_string += """    int x =arc4random()%100;
    int y =arc4random()%100;
"""
        for i  in range(30):
            if i == random_insert_order:
                random_names = random_function_name
                codes1 = f'\n\t//call {random_names}\n\tif (y + {i} >= 30 || x * (x + 1) % 2 == 0) '
            else:
                if i < len(unused_function_name_list):
                    random_names = unused_function_name_list[i]
                else:
                    continue
                codes1 = f'\n\t//call {random_names}\n\tif (y + {i} >= 30 && x * (x + 1) % 2 == 0) '
            insert_string += codes1
            insert_string += '''{'''
            insert_string += f'\n\t\t[self performSelector:@selector({random_names}) withObject:nil afterDelay:0.1];'
            insert_string += '''\n\t}'''
        insert_string += '''\n}'''

        # proxy obfuscate funciton that call from initialize function
        insert_string += f'\n//call {random_function_name}'
        insert_string += f'\n+ (void) {random_function_name}\n'
        insert_string += '{\n'
        insert_string += """    int x =arc4random_uniform(100);
    int y =arc4random_uniform(100);
                    """
        for real_f_name, obfuscate_f_name in dic_names.items():

            insert_string += '''\n\tif (y > 50 && x * (x + 1) % 2 == 0) {'''
            if real_f_name in function_used:
                insert_string += f'\n\t\t[self performSelector:@selector(l_{obfuscate_f_name}) withObject:nil afterDelay:0.1];'
            else:
                insert_string += f'\n\t\t[self performSelector:@selector(l_{obfuscate_f_name}) withObject:nil afterDelay:0.1];'
            insert_string += '''\n\t}else if ( y > 50 || x * (x + 1) % 2 == 0) {'''
            insert_string += f'\n\t\t[self performSelector:@selector(l_{obfuscate_f_name}) withObject:nil afterDelay:0.1];\n'
            insert_string += '''\t}\n'''
        insert_string += '''}\n'''

        # many obfuscate funciton implement will call by proxy obfuscate funciton
        for real_f_name, obfuscate_f_name in dic_names.items():
            insert_string += f'\n\n//call {real_f_name}'
            insert_string += f'\n+ (void) l_{obfuscate_f_name}\n'
            insert_string += '''{'''
            insert_string += """\n\tint x =arc4random_uniform(100);
    int y =arc4random_uniform(100);
                                """
            if real_f_name in function_used:
                insert_string += '''{
    const char * v1;
    if (x * (x + 1) % 2 == 0) {
        v1 = "r1u1n44";'''
                insert_string += '''
        dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{'''
                insert_string += f'\n\t\t\tbool temp_jbs = [{obfuscate_ios_security_suite} {obfuscate_f_name}];'
                print(" @ real anicheck funciton name = "+obfuscate_f_name)
                insert_string += '''\n\t\t\tif (temp_jbs) {
                dispatch_async(dispatch_get_main_queue(), ^{\n'''
                insert_string += f'\t\t\t\t\tNSLog(@"0xa{count}");\n'
                insert_string += '''                    exit(1);\n\t\t\t\t});\n\t\t\t}
        });'''
                insert_string += f'\n\t\t[self performSelector:@selector(l_{obfuscate_f_name}) withObject:nil afterDelay:6];\n'
                insert_string += '''\t}'''
                insert_string += '''else if ( y > 50 || x * (x + 1) % 2 == 0) {
        x = arc4random()%100;
        y = arc4random()%100;
    }
}'''
                count += 1
            else:
                insert_string += '''
    const char * v1;
    if (y > 50 && x * (x + 1) % 2 == 0) {
        v1 = "r1u1n44";
        dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
                dispatch_async(dispatch_get_main_queue(), ^{
                    int a = arc4random()%100;
                    int b = arc4random()%100;
                });
        });
    }
    else if ( y > 50 || x * (x + 1) % 2 == 0) {
        x = arc4random()%100;
        y = arc4random()%100;
    }
    \n'''
            insert_string += '''}'''

        # many obfuscate funciton implement will call by proxy obfuscate funciton
        for unused_f_name in unused_function_name_list:
            insert_string += f'\n\n//call {unused_f_name}'
            insert_string += f'\n+ (void) {unused_f_name}\n'
            insert_string += '''{'''
            insert_string += """\n\tint x =arc4random_uniform(100);
        int y =arc4random_uniform(100);
                                    """
            insert_string += '''
        const char * v1;
        if (y > 50 && x * (x + 1) % 2 == 0) {
            v1 = "r1u1n44";
            dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
                    dispatch_async(dispatch_get_main_queue(), ^{
                        int a = arc4random()%100;
                        int b = arc4random()%100;
                    });
            });
        }
        else if ( y > 50 || x * (x + 1) % 2 == 0) {
            x = arc4random()%100;
            y = arc4random()%100;
        }
        \n'''
            insert_string += '''}'''

        insert_string += '''\n@end'''

        fd.writelines(insert_string)

@click.group()
def cli():
    pass

@click.command()
@click.option('--source_class_name', '-s', help='like UnityAppController that inherit from UIApplicationDelegate')
@click.option('--dic_path', '-d', help='swiftshield obfuscate output file path')
@click.option('--obfs_cfg_path', '-c', help='llvm obfuscate config output file path')
def obfuscate(source_class_name, dic_path, obfs_cfg_path):
    name_dic = {}
    with open(dic_path, 'r') as f_dic:
        for line in f_dic:
            if '===>' in line:
                name_array = line.strip().split("===>")
                name_dic[name_array[0].strip().replace(" ", '')] = name_array[1].strip().replace(" ", '')
    random_function_name = create_flattern_funs_json(name_dic, obfs_cfg_path)
    random_unused_function_name = create_unused_funs(30)
    targety_file_name = "NiceWay"
    generate_codes_h(targety_file_name, source_class_name)
    generate_codes_mm(name_dic, random_function_name, targety_file_name, source_class_name, random_unused_function_name)

cli.add_command(obfuscate)

if __name__ == '__main__':
    cli()
