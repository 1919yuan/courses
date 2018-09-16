(define (fail) (panic "Top level fail"))

(define (a-boolean)
 (call-with-current-continuation
  (lambda (c)
   (let ((saved-fail fail))
    (set! fail (lambda () (set! fail saved-fail) (c #f)))
    #t))))

(define (all-values thunk)
 (let ((values '()))
  (call-with-current-continuation
   (lambda (c)
    (let ((saved-fail fail))
     (set! fail (lambda () (set! fail saved-fail) (c (reverse values))))
     (set! values (cons (thunk) values))
     (fail))))))

(define (either thunk1 thunk2) ((if (a-boolean) thunk1 thunk2)))

(define (an-integer-between low high)
 (when (> low high) (fail))
 (either (lambda () low) (lambda () (an-integer-between (+ low 1) high))))

(define (pythagorean-triples n)
 (all-values
  (lambda ()
   (let ((a (an-integer-between 1 n))
	 (b (an-integer-between 1 n))
	 (c (an-integer-between 1 n)))
    (unless (= (+ (* a a) (* b b)) (* c c)) (fail))
    (list a b c)))))
