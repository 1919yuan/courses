;;; Problem 1.

(define (attacks? qi qj delta-rows)
 (or (= qi qj) (= (abs (- qi qj)) delta-rows)))

(define (check-queens new-column old-columns)
 (for-each-indexed
  (lambda (old-column i)
   (when (attacks? new-column old-column (+ i 1)) (fail)))
  old-columns))

(define (place-n-queens-by-backtracking n)
 (define (loop columns)
  (unless (= (length columns) n)
   (let ((column (an-integer-between 0 (- n 1))))
    (check-queens column columns)
    (place-queen (length columns) column)
    (loop (cons column columns)))))
 (loop '()))

;;; Problem 2.

(define (assert-unary-constraint-gfc! constraint x)
 (restrict-domain!
  x (remove-if-not (lambda (xe) (constraint xe))
		   (domain-variable-domain x))))

(define (assert-binary-constraint-gfc! constraint x y)
 (attach-after-demon!
  (lambda ()
   (when (bound? x)
    (restrict-domain!
     y (remove-if-not (lambda (ye) (constraint (binding x) ye))
		      (domain-variable-domain y)))))
  x)
 (attach-after-demon!
  (lambda ()
   (when (bound? y)
    (restrict-domain!
     x (remove-if-not (lambda (xe) (constraint xe (binding y)))
		      (domain-variable-domain x)))))
  y))

(define (assert-unary-constraint-ac! constraint x)
 (restrict-domain!
  x (remove-if-not (lambda (xe) (constraint xe))
		   (domain-variable-domain x))))

(define (assert-binary-constraint-ac! constraint x y)
 (attach-after-demon!
  (lambda ()
   (restrict-domain!
    y (remove-if-not (lambda (ye)
		      (some (lambda (xe) (constraint xe ye))
			    (domain-variable-domain x)))
		     (domain-variable-domain y))))
  x)
 (attach-after-demon!
  (lambda ()
   (restrict-domain!
    x (remove-if-not (lambda (xe)
		      (some (lambda (ye) (constraint xe ye))
			    (domain-variable-domain y)))
		     (domain-variable-domain x))))
  y))

;;; FOR-EACH-N, MAKE-VECTOR, VECTOR-REF, VECTOR-SET!, VECTOR->LIST

(define (place-n-queens-by-constraints n)
 (let ((columns (make-vector n)))
  (for-each-n
   (lambda (i)
    (let ((domain-variable (create-domain-variable (enumerate n))))
     (vector-set! columns i domain-variable)
     (attach-after-demon!
      (lambda ()
       (when (bound? domain-variable)
	(place-queen i (binding domain-variable))))
      domain-variable)))
   n)
  (for-each-n
   (lambda (i)
    (for-each-n
     (lambda (j)
      (when (> j i)
       (assert-constraint!
	(lambda (column1 column2) (not (attacks? column1 column2 (- j i))))
	(list (vector-ref columns i) (vector-ref columns j)))))
     n))
   n)
  (csp-solution (vector->list columns) first)))
