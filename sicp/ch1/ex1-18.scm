(define (mult x y)
  (cond ((= y 0) 0)
        ((odd? y) (+ x (* 2 (mult x (/ (- y 1) 2)))))
        (else (* 2 (mult x (/ y 2))))))