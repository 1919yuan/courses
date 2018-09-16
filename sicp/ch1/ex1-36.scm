(define (fixed-point f first-guess)
  (let ((tolerance 0.00001))
    (define (close-enough? v1 v2)
      (< (abs (- v1 v2)) tolerance))
    (define (try guess)
      (let ((next (f guess)))
        (newline)
        (display next)
        (if (close-enough? guess next)
            next
            (try next))))
    (try first-guess)))

(define (compute-x-to-x-1000 average-damping-p)
  (fixed-point (lambda (x)
                 (let ((y (/ (log 1000) (log x))))
                   (if average-damping-p
                       (/ (+ x y) 2)
                       y))) 4))
