(define (pascal-x-y x y)
  (cond
   ((< x 0) (error "Incorrect arguments."))
   ((< y 0) 0)
   ((> y x) 0)
   ((= x 0) 1)
   (else (+ (pascal-x-y (- x 1) (- y 1)) (pascal-x-y (- x 1) y)))))

(define (pascal n)
  (define (pascal-iter x)
    (if (= x 0)
        (list (pascal-x-y n 0))
        (append (pascal-iter (- x 1)) (list (pascal-x-y n x)))))
  (pascal-iter n))
