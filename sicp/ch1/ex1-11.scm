(define (f n)
  (define (f-iter a b c iter)
    (if (= iter 0)
        c
        (f-iter (+ a (* 2 b) (* 3 c)) a b (- iter 1))))
  (f-iter 2 1 0 n))
