;;; A formula omega is
;;; a proposition,
;;; (not phi), where phi is a formula, 
;;; (and phi psi), where phi and psi are formulas,
;;; (or phi psi), where phi and psi are formulas,
;;; (implies phi psi), where phi and psi are formulas, or
;;; (iff phi psi), where phi and psi are formulas.

(define (inconsistent? m1 m2)
 (some (lambda (binding1)
	(some (lambda (binding2)
	       (and (eq? (first binding1) (first binding2))
		    (not (eq? (second binding1) (second binding2)))))
	      m2))
       m1))

(define (models omega)
 (if (symbol? omega)
     (list (list (list omega #t)))
     (case (first omega )
      ((not)
       (let ((omega (second omega)))
	(if (symbol? omega)
	    (list (list (list omega #f)))
	    (case (first omega)
	     ((not) (models (second omega)))
	     ((and) (models `(or (not ,(second omega))
				 (not ,(third omega)))))
	     ((or) (models `(and (not ,(second omega))
				 (not ,(third omega)))))
	     ((implies) (models `(and ,(second omega)
				      (not ,(third omega)))))
	     ((iff) (models
		     `(or (not (implies ,(second omega) ,(third omega)))
			  (not (implies ,(third omega) ,(second omega))))))
	     (else (panic "Invalid formula"))))))
      ((and)
       (let ((models1 (models (second omega)))
	     (models2 (models (third omega))))
	(reduce
	 union
	 (map (lambda (m1)
	       (remove
		'inconsistent
		(map (lambda (m2)
		      (if (inconsistent? m1 m2)
			  'inconsistent
			  (union m1 m2)))
		     models2)))
	      models1)
	 '())))
      ((or) (union (models (second omega))
		   (models (third omega))))
      ((implies) (models `(or (not ,(second omega)) ,(third omega))))
      ((iff) (models `(and (implies ,(second omega) ,(third omega))
			   (implies ,(third omega) ,(second omega)))))
      (else (panic "Invalid formula")))))

(define (list->conjunction sigma)
 (if (null? (rest sigma))
     (first sigma)
     `(and ,(first sigma) ,(list->conjunction (rest sigma)))))

(define (entails? sigma phi)
 (null? (models (list->conjunction (union sigma (list `(not ,phi)))))))
