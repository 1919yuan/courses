(define (cont-frac n d k)
  (define (n-next i)
    (n (+ i 1)))
  (define (d-next i)
    (d (+ i 1)))
  (if (= k 0)
      0
      (/ (n 1)
         (+ (d 1) (cont-frac n-next d-next (- k 1))))))

(define (cont-frac-iter n d k)
  (define (iter result i)
    (if (= i 0)
        result
        (iter (/ (n i) (+ (d i) result)) (- i 1))))
  (iter 0 k))
