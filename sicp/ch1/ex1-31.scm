(define (product term a next b)
  (if (> a b)
      1
      (* (term a)
         (product term (next a) next b))))

(define (product-iter term a next b)
  (define (iter result a)
    (if (> a b)
        result
        (iter (* result (term a)) (next a))))
  (iter 1 a))

(define (compute-pi n)
  (define (term i)
    (/ (* 2 (quotient (+ i 2) 2))
       (- (* 2 (quotient (+ i 3) 2)) 1)))
  (* 4 (product term 1 (lambda (x) (+ x 1)) n)))
