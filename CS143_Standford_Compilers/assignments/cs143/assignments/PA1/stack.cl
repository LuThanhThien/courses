(* 
 * CS164 / CS143
 * Programming Assignment 1
 * Simple stack machine skeleton
 *)

class List {
   -- Define operations on empty lists.

   isNil() : Bool { true };

   head()  : String { { abort(); ""; } };

   tail()  : List { { abort(); self; } };

   length() : Int { 0 };

   pop(id: Int) : List { { abort(); self; } };

   get(id: Int) : String { { abort(); ""; } };

   set(id: Int, i: String) : List { { abort(); self; } };

   swap(id1: Int, id2: Int) : List { { abort(); self; } };

   cons(i : String) : List {
      (new Cons).init(i, self)
   };
};

class Cons inherits List {
   -- Cons of list
   
   item: String;
   rest: List;

   isNil() : Bool { false };

   head() : String { item };

   tail() : List { rest };

   init(it: String, rst: List) : List {
      {
         item <- it;
         rest <- rst;
         self;
      }
   };

   length() : Int { 
      if rest.isNil() then 1 else 1 + rest.length() fi
   };

   pop(id: Int) : List {
      if not (id < length()) then { abort(); self; }
      else if id  = length() - 1 then rest
      else if id = length() - 2 then
      {
         let out : List <- rest in 
         {
            rest <- rest.tail();
            self;
         };
      }
      else { rest <- rest.pop(id); self; }
      fi fi fi
   };

   get(id: Int) : String { 
      if not (id < length()) then { abort(); ""; }
      else if id = length() - 1 then item
      else rest.get(id) 
      fi fi
   };

   set(id: Int, i: String) : List {
      if not (id < length()) then { abort(); self; }
      else if id = length() - 1 then { item <- i; self; }
      else { rest <- rest.set(id, i); self; }
      fi fi
   };

   swap(id1: Int, id2: Int) : List {
      {
         -- If indices are equal, nothing to do
         if id1 = id2 then self
         else
            let 
               len : Int <- length(),
               lo  : Int <- (if id1 < id2 then id1 else id2 fi),
               hi  : Int <- (if id1 < id2 then id2 else id1 fi)
            in
               if not (hi < len) then        -- bounds check
                  { abort(); self; }
               else
                  -- Step 1: extract items
                  let a : String <- get(lo) in
                  let b : String <- get(hi) in
                  {
                     let t : List <- self in {
                        t <- t.set(hi, a);
                        t <- t.set(lo, b);
                        t;
                     };
                  }
               fi
         fi;
      }
   };

};

class StackCommand {
   -- Generic definition of command

   eval(l: List, c: String) : List { { abort(); l; } };

};

class PushCommand inherits StackCommand {

   eval(l: List, c: String) : List {
      {
         l <- l.cons(c);
         l; 
      }
   };

};

class PrintCommand inherits StackCommand {

   print_stack(l: List) : Object {
      if l.isNil() then (new IO).out_string("")
      else 
      {
         (new IO).out_string(l.head());
         (new IO).out_string("\n");
         print_stack(l.tail());
         l;
      } fi
   };

   eval(l: List, c: String) : List {
      {
         print_stack(l);
         l;
      }
   };

};

class EvalCommand inherits StackCommand {

   find_next_int(l: List): Int { 
      let id : Int <- l.length() - 1 in 
         if l.head() = "+" then find_next_int(l.tail())
         else if l.head() = "s" then find_next_int(l.tail())
         else id
         fi fi
   };

   find_int(l: List) : Int { 
      (new A2I).a2i(l.get(find_next_int(l)))
   };

   pop_int(l: List) : List { 
      l.pop(find_next_int(l))
   };

   eval(l: List, c: String) : List {
      -- eval
      if l.isNil() then l
      else if l.head() = "+" then 
      {
         l <- l.pop(l.length() - 1);
         -- find and pop 2 int
         let a : Int <- find_int(l) in 
         {
            l <- pop_int(l);
            let b : Int <- find_int(l) in 
            {
               l <- pop_int(l);
               l <- l.cons((new A2I).i2a(a + b));
            };
         };
         l;
      }
      else if l.head() = "s" then 
      {
         l <- l.pop(l.length() - 1);
         l <- l.swap(l.length() - 1, l.length() -2);
         l;
      }
      else l
      fi fi fi
   };

};


class Main inherits IO {

   list: List;
   exit : Bool;

   main() : Object {
      {
         list <- new List;
         let line : String <- in_string() in
         while not (line.length() = 0) loop       
            {
               exit <- parse(line);
               line <- (if exit then "" else in_string() fi);       
            }
         pool;
      }
   };

   parse(command: String): Bool {
      {
         out_string(">").out_string(command).out_string("\n");
         if command = "e" then { list <- (new EvalCommand).eval(list, command); false; }
         else if command = "d" then { list <- (new PrintCommand).eval(list, command); false; }
         else if command = "x" then true
         else { list <- (new PushCommand).eval(list, command); false; }
         fi fi fi;
      }
   };

};