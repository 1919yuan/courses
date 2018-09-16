(define (sum term a next b)
  (if (> a b)
      0
      (+ (term a)
         (sum term (next a) next b))))

(define (integral f a b dx)
  (define (add-dx x) (+ x dx))
  (* (sum f (+ a (/ dx 2.0)) add-dx b) dx))

(define (simpson-integral f a b n)
  (let ((h (/ (- b a) n)))
    (define (level i)
      (cond
       ((or (= 0 i) (= n i))
        (/ h 3))
       ((odd? i)
        (* h (/ 4 3)))
       ((even? i)
        (* h (/ 2 3)))
       (else 0)))
    (define (term i)
      (* (level i) (f (+ a (* i h)))))
    (define (next i) (+ i 1))
    (sum term 0 next n)))

(define (cube x)
  (* x x x))
