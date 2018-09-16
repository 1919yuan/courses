(define *derivative-rules*
 '(((derivative x) -~-> 1)
   ((derivative (+ e1 e2)) -~-> (+ (derivative e1) (derivative e2)))
   ((derivative (* e1 e2))
    -~->
    (+ (* e1 (derivative e2)) (* e2 (derivative e1))))
   ((derivative (expt e1 e2)) -~-> (* e2 (expt e1 (- e2 1)) (derivative e1)))
   ((derivative e) -~-> 0)))

(define (simplify e) (rewrite e (append *simplify-rules* *derivative-rules*)))
