(define (calculate-+ arguments) (reduce + arguments 0))

(define (calculate-- arguments)
 (cond ((null? arguments) (panic "- cannot take zero arguments"))
       ((= (length arguments) 1) (- (first arguments)))
       (else (- (first arguments) (reduce + (rest arguments) 0)))))

(define (calculate-* arguments) (reduce * arguments 1))

(define (calculate-/ arguments)
 (cond ((null? arguments) (panic "/ cannot take zero arguments"))
       ((= (length arguments) 1) (/ (first arguments)))
       (else (/ (first arguments) (reduce * (rest arguments) 1)))))

(define (calculate-expt arguments)
 (if (= (length arguments) 2)
     (expt (first arguments) (second arguments))
     (panic "EXPT must take exactly two arguments")))

(define (calculate-sqrt arguments)
 (if (= (length arguments) 1)
     (sqrt (first arguments))
     (panic "SQRT must take exactly one argument")))

(define (calculate e)
 (cond ((number? e) e)
       ((and (list? e) (not (null? e)))
	(case (first e)
	 ((+) (calculate-+ (map calculate (rest e))))
	 ((-) (calculate-- (map calculate (rest e))))
	 ((*) (calculate-* (map calculate (rest e))))
	 ((/) (calculate-/ (map calculate (rest e))))
	 ((expt) (calculate-expt (map calculate (rest e))))
	 ((sqrt) (calculate-sqrt (map calculate (rest e))))
	 (else (panic "Invalid expression"))))
       (else (panic "Invalid expression"))))
