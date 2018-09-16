(load "ex1-20.scm")
(load "ex1-24.scm")

(define (filtered-accumulate combiner null-value term a next b
                             predicate)
  (if (> a b)
      null-value
      (let ((remaining
             (filtered-accumulate combiner null-value term (next a) next b
                                  predicate)))
        (if (predicate a)
            (combiner remaining (term a))
            remaining))))

(define (sum-square-of-prime-in-range a b)
  (filtered-accumulate + 0
                       (lambda (x) (* x x))
                       a (lambda (x) (+ x 1)) b
                       (lambda (x) (fast-prime? x 10))))

(define (product-of-relative-prime n)
  (define (predicate x)
    (and (number? x)
         (> x 0)
         (< x n)
         (= 1 (gcd x n))))
  (filtered-accumulate * 1 identity 1 (lambda (x) (+ x 1)) (- n 1)
                       predicate))
