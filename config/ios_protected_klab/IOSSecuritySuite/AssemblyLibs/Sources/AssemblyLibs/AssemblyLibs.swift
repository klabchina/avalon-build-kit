import PtraceC
public struct FuncLibs {
    //disable attach by ptrace
    public static func set_pgdb_interface(y : inout Int) {
        var v1: String = ""
        var x = Int.random(in: 1..<100)
        y = Int.random(in: 1..<100)
        if (x * (x + 1) % 2 == 0)
        {
            v1 = "run";
            set_pgdb(1)
        }
        else if ( y > 10 || x * (x + 1) % 2 == 0)
        {
            v1 = "don't run it";
            set_pgdb(1)
        }
        
        x = Int.random(in: 1..<1000)
        y = Int.random(in: 1..<1000)
        if (x * (x + 1) % 2 == 0)
        {
            v1 = "run12121";
            print(v1)
        }
        else if ( y > 10 || x * (x + 1) % 2 == 0)
        {
            v1 = "don't run it222";
            print(v1)
        }
    }
}
