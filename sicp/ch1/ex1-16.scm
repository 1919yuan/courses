(define (fast-expt x n)
  (define (fast-expt-iter x n a)
    (if (= n 0)
        a
        (if (odd? n)
            (fast-expt-iter (* x x) (/ (- n 1) 2) (* a x))
            (fast-expt-iter (* x x) (/ n 2) a))))
  (fast-expt-iter x n 1))