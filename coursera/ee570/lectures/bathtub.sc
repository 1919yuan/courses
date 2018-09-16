(define (adjacent? x y)
 (or
  (equal? x y)
  (and (landmark? x) (range? y) (or (eqv? x (first y)) (eqv? x (second y))))
  (and (range? x) (landmark? y) (or (eqv? (first x) y) (eqv? (second x) y)))))

(define *a-qs* '(0 (0 full) full (full inf) inf))
(define *n-qs* '(minf (minf 0) 0 (0 inf) inf))
(define *i-qs* '(0 (0 c) c (c inf) inf))
(define *o-qs* '(minf (minf 0) 0 (0 inf) inf))
(define *p-qs* '(0 (0 inf) inf))
(define *l-qs* '(0 (0 top) top (top inf) inf))
(define *a=a+n*
 '((() () (0) ((0 full) full (full inf)) (inf))
   (() (0 (0 full)) ((0 full)) ((0 full) full (full inf)) (inf))
   (() (0 (0 full)) (full) ((full inf)) (inf))
   (() (0 (0 full) full (full inf)) ((full inf)) ((full inf)) (inf))
   (#t (inf) (inf) (inf) (inf))))
(define *n=i-o*
 '(((inf) ((0 inf)) (0) ((minf 0)) (minf))
   ((inf) ((0 inf)) ((0 inf)) ((minf 0) 0 (0 inf)) (minf))
   ((inf) ((0 inf)) ((0 inf)) ((minf 0) 0 (0 inf)) (minf))
   ((inf) ((0 inf)) ((0 inf)) ((minf 0) 0 (0 inf)) (minf))
   ((inf) (inf) (inf) (inf) #t)))
(define *o=m+-of-p* '((0) ((0 inf)) (inf)))
(define *p=m+-of-l* '((0) ((0 inf)) ((0 inf)) ((0 inf)) (inf)))
(define *l=m+-of-a* '((0) ((0 top)) (top) ((top inf)) (inf)))

(define (unary? y x c)
 (lambda (ye xe)
  (let ((e (list-ref c (position xe x))))
   (or (eq? e #t) (not (not (member ye e)))))))

(define (binary? z x y c)
 (lambda (ze xe ye)
  (let ((e (list-ref (list-ref c (position xe x)) (position ye y))))
   (or (eq? e #t) (not (not (member ze e)))))))

(define (for-each-entry-but-last-column p a)
 (let ((m (matrix-rows a)) (n (matrix-columns a)))
  (for-each-n (lambda (i) (for-each-n (lambda (j) (p i j m n)) (- n 1))) m)))

(define (for-each-interval-column p a)
 (let ((n (matrix-columns a)))
  (for-each-n (lambda (j) (when (interval? j) (p j n))) n)))

(define (for-each-instant-column p a)
 (let ((n (matrix-columns a)))
  (for-each-n (lambda (j) (when (instant? j) (p j n))) n)))

(define (condition1! a)
 ;; Continuity
 (for-each-entry-but-last-column
  (lambda (i j m n)
   (assert-constraint!
    adjacent? (list (matrix-ref a i j) (matrix-ref a i (+ j 1)))))
  a))

(define (condition2! a)
 ;; Landmarks
 (for-each-entry-but-last-column
  (lambda (i j m n)
   (if (interval? j)
       (assert-constraint!
	(lambda (x y) (implies (landmark? x) (equal? x y)))
	(list (matrix-ref a i j) (matrix-ref a i (+ j 1))))
       (assert-constraint!
	(lambda (x y) (implies (landmark? y) (equal? x y)))
	(list (matrix-ref a i j) (matrix-ref a i (+ j 1))))))
  a))

(define (condition3! a quantity-derivative-pairs)
 ;; Stationarity
 (for-each
  (lambda (quantity-derivative-pair)
   (for-each-interval-column
    (lambda (j n)
     (assert-constraint!
      (lambda (x y) (implies (landmark? x) (equal? y 0)))
      (list (matrix-ref a (first quantity-derivative-pair) j)
	    (matrix-ref a (second quantity-derivative-pair) j))))
    a))
  quantity-derivative-pairs))

(define (condition4! a)
 ;; Merging identical adjacent intervals
 (for-each-instant-column
  (lambda (j n)
   (when (every-vector (lambda (x y z)
			(and (equal? (binding x) (binding y))
			     (equal? (binding y) (binding z))))
		       (matrix-column-ref a (- j 1))
		       (matrix-column-ref a j)
		       (matrix-column-ref a (+ j 1)))
    (fail)))
  a))

(define (condition5! a quantity-derivative-pairs)
 ;; Qualitative Mean-Value Theorem
 (for-each
  (lambda (quantity-derivative-pair)
   (for-each-interval-column
    (lambda (j n)
     (unless (= j 0)
      (assert-constraint!
       (binary? *a-qs* *a-qs* *n-qs* *a=a+n*)
       (list (matrix-ref a (first quantity-derivative-pair) j)
	     (matrix-ref a (first quantity-derivative-pair) (- j 1))
	     (matrix-ref a (second quantity-derivative-pair) j))))
     (unless (= j (- n 1))
      (assert-constraint!
       (binary? *a-qs* *a-qs* *n-qs* *a=a+n*)
       (list (matrix-ref a (first quantity-derivative-pair) (+ j 1))
	     (matrix-ref a (first quantity-derivative-pair) j)
	     (matrix-ref a (second quantity-derivative-pair) j)))))
    a))
  quantity-derivative-pairs))

(define (condition6! a quantity-derivative-pairs)
 ;; Termination
 (for-each-interval-column
  (lambda (j n)
   (unless (or (= j 0) (= j (- n 1)))
    (when (every
	   (lambda (quantity-derivative-pair)
	    (equal?
	     (binding (matrix-ref a (second quantity-derivative-pair) j)) 0))
	   quantity-derivative-pairs)
     (fail))))
  a))

(define (matrix-solution a)
 (csp-solution (reduce append (vector->list (map-vector vector->list a)) '())
	       first))

(define (solve-bathtub-by-backtracking n)
 (message "Unimplemented")
 (abort))

(define (solve-bathtub-by-constraints n)
 (let ((a (make-matrix 6 n)))
  (for-each-n
   (lambda (j)
    (matrix-set! a 0 j (create-domain-variable *n-qs*)) ; n, a-dot
    (matrix-set! a 1 j (create-domain-variable *i-qs*)) ; i
    (matrix-set! a 2 j (create-domain-variable *o-qs*)) ; o
    (matrix-set! a 3 j (create-domain-variable *p-qs*)) ; p
    (matrix-set! a 4 j (create-domain-variable *l-qs*)) ; l
    (matrix-set! a 5 j (create-domain-variable *a-qs*))) ; a
   n)
  (for-each-n
   (lambda (i)
    (for-each-n
     (lambda (j)
      (let ((variable (matrix-ref a i j)))
       (attach-after-demon!
	(lambda ()
	 (when (bound? variable) (draw-quantity (binding variable) i j)))
	variable)))
     n))
   6)
  ;; Differential equations
  (for-each-n
   (lambda (j)
    (assert-constraint!
     (binary? *n-qs* *i-qs* *o-qs* *n=i-o*) ; n=i-o
     (list (matrix-ref a 0 j) (matrix-ref a 1 j) (matrix-ref a 2 j)))
    (assert-constraint!
     (unary? *o-qs* *p-qs* *o=m+-of-p*) ; o=M+(p)
     (list (matrix-ref a 2 j) (matrix-ref a 3 j)))
    (assert-constraint!
     (unary? *p-qs* *l-qs* *p=m+-of-l*) ; p=M+(l)
     (list (matrix-ref a 3 j) (matrix-ref a 4 j)))
    (assert-constraint!
     (unary? *l-qs* *a-qs* *l=m+-of-a*) ; l=M+(a)
     (list (matrix-ref a 4 j) (matrix-ref a 5 j))))
   n)
  ;; Initial conditions
  ;; i=c
  (for-each-n
   (lambda (j)
    ;; in order for a to be 0 in first interval, i must be 0 in the first
    ;; interval
    ;; by condition2, i must be 0 in the first instant
    ;; by condition1, i can only increase to (0 c) in the second interval
    (when (> j 2)
     (assert-constraint!
      (lambda (x) (equal? x 'c)) (list (matrix-ref a 1 j)))))
   n)
  ;; a(0)=0
  (assert-constraint! (lambda (x) (equal? x 0)) (list (matrix-ref a 5 0)))
  (condition1! a)
  (condition2! a)
  (condition3! a '((5 0)))
  (condition5! a '((5 0)))
  (matrix-solution a)
  (condition4! a)
  (condition6! a '((5 0)))))
