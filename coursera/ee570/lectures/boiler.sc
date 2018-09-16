;;; instruction is (load r x)
;;;                (store r x)
;;;                null?
;;;                first
;;;                rest
;;;                cons
;;;                (jump l)
;;;                (jump-if-false l)
;;; ROM-contents is
;;; ([pc] (ROM-address1 instruction1) [pc] (ROM-address2 instruction2) ...)
;;; RAM-contents is is ((a v) (b v) (0 v) ... (15 v))
;;; i is an instruction
;;; j is an (ROM-address instruction)
;;; k is RAM contents
;;; l is a ROM address
;;; m is a (RAM-address/register value)
;;; r is a register
;;; v is a value
;;; x is a RAM address
;;; machine state is (ROM-contents RAM-contents)

(define *boilerchip*
 '(;; load
   (((j1... pc (l1 (load r x)) j2...) (m1... (r v1) m2... (x v2) m3...))
    -~->
    ((j1... (l1 (load r x)) pc j2...) (m1... (r v2) m2... (x v2) m3...)))
   ;; store
   (((j1... pc (l1 (store r x)) j2...) (m1... (r v1) m2... (x v2) m3...))
    -~->
    ((j1... (l1 (store r x)) pc j2...) (m1... (r v1) m2... (x v1) m3...)))
   ;; null?
   (((j1... pc (l1 null?) j2...) ((a ()) m1...))
    -~->
    ((j1... (l1 null?) pc j2...) ((a #t) m1...)))
   (((j1... pc (l1 null?) j2...) ((a #t) m1...))
    -~->
    ((j1... (l1 null?) pc j2...) ((a #f) m1...)))
   (((j1... pc (l1 null?) j2...) ((a #f) m1...))
    -~->
    ((j1... (l1 null?) pc j2...) ((a #f) m1...)))
   (((j1... pc (l1 null?) j2...) ((a (v1 v...)) m1...))
    -~->
    ((j1... (l1 null?) pc j2...) ((a #f) m1...)))
   ;; first
   (((j1... pc (l1 first) j2...) ((a (v1 v...)) m1...))
    -~->
    ((j1... (l1 first) pc j2...) ((a v1) m1...)))
   ;; rest
   (((j1... pc (l1 rest) j2...) ((a (v1 v...)) m1...))
    -~->
    ((j1... (l1 rest) pc j2...) ((a (v...)) m1...)))
   ;; cons
   (((j1... pc (l1 cons) j2...) ((a v1) (b (v...)) m1...))
    -~->
    ((j1... (l1 cons) pc j2...) ((a (v1 v...)) (b (v...)) m1...)))
   ;; jump
   (((j1... (l1 i) j2... pc (l2 (jump l1)) j3...) k)
    -~->
    ((j1... pc (l1 i) j2... (l2 (jump l1)) j3...) k))
   (((j1... pc (l2 (jump l1)) j2... (l1 i) j3...) k)
    -~->
    ((j1... (l2 (jump l1)) j2... pc (l1 i) j3...) k))
   (((j1... pc (l1 (jump l1)) j2...) k)
    -~->
    ((j1... pc (l1 (jump l1)) j2...) k))
   ;; jump-if-false
   (((j1... (l1 i) j2... pc (l2 (jump-if-false l1)) j3...) ((a #f) m1...))
    -~->
    ((j1... pc (l1 i) j2... (l2 (jump-if-false l1)) j3...) ((a #f) m1...)))
   (((j1... pc (l2 (jump-if-false l1)) j2... (l1 i) j3...) ((a #f) m1...))
    -~->
    ((j1... (l2 (jump-if-false l1)) j2... pc (l1 i) j3...) ((a #f) m1...)))
   (((j1... pc (l1 (jump-if-false l1)) j2...) ((a #f) m1...))
    -~->
    ((j1... pc (l1 (jump-if-false l1)) j2...) ((a #f) m1...)))

   (((j1... pc (l2 (jump-if-false l1)) j2...) ((a #t) m1...))
    -~->
    ((j1... (l2 (jump-if-false l1)) pc j2...) ((a #t) m1...)))
   (((j1... pc (l2 (jump-if-false l1)) j2...) ((a (v...)) m1...))
    -~->
    ((j1... (l2 (jump-if-false l1)) pc j2...) ((a (v...)) m1...)))))

(define (pattern-variable? pattern) (memq pattern '(i k l1 l2 m r v1 v2 x)))

(define (pattern-list-variable? pattern)
 (memq pattern '(j1... j2... j3... m1... m2... m3... v...)))

(define (plus x y) (if (null? x) y (plus (rest x) (cons #t y))))

(define *plus-ROM*
 ;; // 0 must be initialized to #t
 ;;     store a 1
 ;;     store b 2
 ;; l1: load a 1
 ;;     null?
 ;;     jump-if-false l2
 ;;     jump l3
 ;; l2: load a 1
 ;;     rest
 ;;     store a 1
 ;;     load a 0
 ;;     load b 2
 ;;     cons
 ;;     store a 2
 ;;     jump l1
 ;; l3: load a 2
 '((n0 (store a 1))
   (n1 (store b 2))
   (n2 (load a 1))
   (n3 null?)
   (n4 (jump-if-false n6))
   (n5 (jump n14))
   (n6 (load a 1))
   (n7 rest)
   (n8 (store a 1))
   (n9 (load a 0))
   (n10 (load b 2))
   (n11 cons)
   (n12 (store a 2))
   (n13 (jump n2))
   (n14 (load a 2))))

(define (initial-state x y)
 `((pc ,@*plus-ROM*) ((a ,x) (b ,y) (0 #t) (1 #f) (2 #f))))

(define (peano-plus x y)
 (length (plus (map (lambda (i) #t) (enumerate x))
	       (map (lambda (i) #t) (enumerate y)))))

(define (simulated-plus x y)
 (length
  (second
   (first
    (second
     (rewrite (initial-state (map (lambda (i) #t) (enumerate x))
			     (map (lambda (i) #t) (enumerate y)))
	      *boilerchip*))))))

(define (theorem1)
 (every (lambda (x)
	 (every (lambda (y) (equal? (peano-plus x y) (simulated-plus x y)))
		*everything*))
	*everything*))

(define *boilerscheme-compiler* '())

(define *bolerscheme-interpreter* '())

(define (compile-boilerscheme boilerscheme-program)
 (extract-compiler-output
  (rewrite (compiler-initial-state boilerscheme-program)
	   *boilerscheme-compiler*)))

(define (simulate-boilerscheme boilerchip-program input)
 (extract-simulator-output
  (rewrite (simulator-initial-state boilerchip-program input)
	   *boilerchip*)))

(define (compile-and-simulate-boilerscheme boilerscheme-program input)
 (simulate-boilerscheme (compile-boilerscheme boilerscheme-program) input))

(define (interpret-boilerscheme boilerscheme-program input)
 (extract-interpreter-output
  (rewrite (interpreter-initial-state boilerscheme-program input)
	   *bolerscheme-interpreter*)))

(define (theorem2)
 (every
  (lambda (boilerscheme-program)
   (every
    (lambda (input)
     (equal? (compile-and-simulate-boilerscheme boilerscheme-program input)
	     (interpret-boilerscheme boilerscheme-program input)))
    *everything*))
  *everything*))
