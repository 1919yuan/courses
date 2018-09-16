(define *simplify-rules*
 '(((+) -~-> 0)
   ((+ e) -~-> e)
   ((+ e 0) -~-> e)
   ((+ 0 e) -~-> e)
   ((+ e1 e2 e3 e...) -~-> (+ e1 (+ e2 (+ e3 e...))))
   ((- e) -~-> (* -1 e))
   ((- e1 e2) -~-> (+ e1 (- e2)))
   ((- e1 e2 e3 e...) -~-> (- e1 (+ e2 e3 e...)))
   ((*) -~-> 1)
   ((* e) -~-> e)
   ((* e 0) -~-> 0)
   ((* 0 e) -~-> 0)
   ((* e 1) -~-> e)
   ((* 1 e) -~-> e)
   ((* e1 e2 e3 e...) -~-> (* e1 (* e2 (* e3 e...))))
   ((/ e) -~-> (expt e -1))
   ((/ e1 e2) -~-> (* e1 (/ e2)))
   ((/ e1 e2 e3 e...) -~-> (/ e1 (* e2 e3 e...)))
   ((expt e 1) -~-> e)
   ((sqrt e) -~-> (expt e 0.5))))

(define (simplify e) (rewrite e *simplify-rules*))
