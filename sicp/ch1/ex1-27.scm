;;; Support for numbers larger than most-positive-fixnum
(require-extension numbers)

(define (square x) (* x x))

(define (expmod base exp m)
  (cond ((= exp 0) 1)
        ((even? exp)
         (remainder (square (expmod base (/ exp 2) m)) m))
        (else (remainder (* base (expmod base (- exp 1) m)) m))))

(define (fermat-test n)
  (define (try-it a)
    (= (expmod a n n) a))
  (define (try-it-iter iter)
    (if (< iter n)
        (if (try-it iter)
            (try-it-iter (+ iter 1))
            #f)
        #t))
  (try-it-iter 0))
