;;; MEMQ

(define (pattern-variable? pattern) (memq pattern '(phi)))

(define (pattern-list-variable? pattern)
 (memq pattern '(phi... phi1... phi2... phi3... psi...)))

(define (inconsistent-bindings? binding1 binding2)
 (and (eq? (first binding1) (first binding2))
      (not (equal? (second binding1) (second binding2)))))

(define (contains-inconsistent-bindings? bindings)
 (and (not (null? bindings))
      (or (some (lambda (remaining-binding)
		 (inconsistent-bindings? (first bindings) remaining-binding))
		(rest bindings))
	  (contains-inconsistent-bindings? (rest bindings)))))

;;; REMOVE-DUPLICATES

(define (merge-bindings bindings1 bindings2)
 (if (or (eq? bindings1 #f) (eq? bindings2 #f))
     #f
     (let ((bindings (remove-duplicates (append bindings1 bindings2))))
      (if (contains-inconsistent-bindings? bindings) #f bindings))))

(define (map-cross-product p l1 l2)
 (reduce append (map (lambda (e1) (map (lambda (e2) (p e1 e2)) l2)) l1) '()))

;;; MAP-N, REMOVEQ

(define (matches pattern expression)
 (cond
  ((pattern-variable? pattern) (list (list (list pattern expression))))
  ((pattern-list-variable? pattern)
   (panic "Pattern cannot consist solely of pattern list variable"))
  ((and (list? pattern) (list? expression))
   (cond ((null? pattern) (if (null? expression) (list '()) '()))
	 ((pattern-list-variable? (first pattern))
	  (let ((n (length expression)))
	   (reduce
	    append
	    (map-n
	     (lambda (i)
	      (removeq
	       #f
	       (map (lambda (bindings)
		     (merge-bindings
		      (list (list (first pattern) (sublist expression 0 i)))
		      bindings))
		    (matches (rest pattern) (sublist expression i n)))))
	     (+ n 1))
	    '())))
	 ((null? expression) '())
	 (else (removeq
		#f
		(map-cross-product
		 merge-bindings
		 (matches (first pattern) (first expression))
		 (matches (rest pattern) (rest expression)))))))
  ((eqv? pattern expression) (list '()))
  (else '())))

(define (match pattern expression)
 (let ((matches (matches pattern expression)))
  (if (null? matches) #f (first matches))))

(define (lookup-pattern-variable pattern-variable bindings)
 (cond ((null? bindings) (panic "Unbound pattern variable"))
       ((eq? pattern-variable (first (first bindings)))
	(second (first bindings)))
       (else (lookup-pattern-variable pattern-variable (rest bindings)))))

(define (instantiate pattern bindings)
 (cond ((pattern-variable? pattern) (lookup-pattern-variable pattern bindings))
       ((pattern-list-variable? pattern)
	(panic "Pattern cannot consist solely of pattern list variable"))
       ((list? pattern)
	(reduce append
		(map (lambda (pattern)
		      (if (pattern-list-variable? pattern)
			  (lookup-pattern-variable pattern bindings)
			  (list (instantiate pattern bindings))))
		     pattern)
		'()))
       (else pattern)))

(define (first-matching-rule e rules)
 (if (null? rules)
     #f
     (let ((bindings (match (first (first rules)) e)))
      (if (eq? bindings #f)
	  (first-matching-rule e (rest rules))
	  (first rules)))))

(define (rewrite e rules)
 (define (rewrite-with-rules e) (rewrite e rules))
 (let* ((e-prime (if (list? e) (map rewrite-with-rules e) e))
	(rule (first-matching-rule e-prime rules)))
  (if (eq? rule #f)
      e-prime
      (rewrite
       (instantiate (third rule) (match (first rule) e-prime)) rules))))

(define *boolean-simplification-rules*
 '(((not #t) -~-> #f)
   ((not #f) -~-> #t)
   ((not (not phi)) -~-> phi)
   ((and) -~-> #t)
   ((and phi) -~-> phi)
   ((and phi... #t psi...) -~-> (and phi... psi...))
   ((and phi... #f psi...) -~-> #f)
   ((and phi1... (and phi2...) phi3...) -~-> (and phi1... phi2... phi3...))
   ((and phi1... phi phi2... phi phi3...)
    -~-> (and phi1... phi phi2... phi3...))
   ((and phi1... phi phi2... (not phi) phi3...) -~-> #f)
   ((and phi1... (not phi) phi2... phi phi3...) -~-> #f)
   ((or) -~-> #f)
   ((or phi) -~-> phi)
   ((or phi... #f psi...) -~-> (or phi... psi...))
   ((or phi... #t psi...) -~-> #t)
   ((or phi1... (or phi2...) phi3...) -~-> (or phi1... phi2... phi3...))
   ((or phi1... phi phi2... phi phi3...) -~-> (or phi1... phi phi2... phi3...))
   ((or phi1... phi phi2... (not phi) phi3...) -~-> #t)
   ((or phi1... (not phi) phi2... phi phi3...) -~-> #t)))

(define (boolean-simplify phi) (rewrite phi *boolean-simplification-rules*))

(define (truth-tables-match? phi phi-prime)
 (every (lambda (truth-assignment)
	 (eq? (boolean-evaluate phi truth-assignment)
	      (boolean-evaluate phi-prime truth-assignment)))
	(all-truth-assignments
	 (unionq (propositions-in phi) (propositions-in phi-prime)))))
