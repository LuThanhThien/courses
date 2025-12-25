(* 
 * CS164 / CS143
 * Programming Assignment 1
 * Simple stack machine skeleton
 *)

class Stack {
   prev : Stack; 
   item : String;
   next : Stack;

   is_void(): Bool {
      item.length() = 0
   };

   is_head() : Bool {
      isvoid prev
   };

   is_tail() : Bool {
      isvoid next
   };

   push_back(i : String) : Stack {
      {
         if is_void() then {
            item <- i;
         }
         else {
            if is_tail() then { 
               next <- new Stack;
               next.link(self);
            } else 0 fi;
            next <- next.push_back(i);
         } fi;
         self;
      }
   };

   pop_front() : Stack {
      {
         if is_head() then
            item <- ""
         else {
            if prev.is_head() then 
               unlink()
            else 0 fi;
         } fi;
         self;
      }
   };

   link(l: Stack): Object {
      prev <- l
   };

   unlink(): Object {
      prev <- void
   };

   print() : Object {
      {
         if not is_void() then 
            (new IO).out_string(item)
         else
            0
         fi;

         if not is_tail() then {
            (new IO).out_string("\n");
            next.print();
         }
         else
            0
         fi;
      }
   };
};

