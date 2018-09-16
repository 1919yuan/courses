;;; MAP-N

(define (initial-board n) (map-n (lambda (i) (map-n (lambda (i) 0) n)) n))

(define (player board)
 (if (zero? (reduce + (map (lambda (row) (reduce + row 0)) board) 0)) 1 -1))

(define (discard-non-empty row)
 (cond ((null? row) '())
       ((zero? (third (first row)))
	(cons (first row) (discard-non-empty (rest row))))
       (else (discard-non-empty (rest row)))))

;;; MAP-INDEXED

(define (moves board)
 (map (lambda (move) (list (first move) (second move)))
      (reduce append
	      (map-indexed
	       (lambda (row i)
		(discard-non-empty
		 (map-indexed (lambda (element j) (list i j element)) row)))
	       board)
	      '())))

(define (list-replace-ith list i x)
 (if (= i 0)
     (cons x (rest list))
     (cons (first list) (list-replace-ith (rest list) (- i 1) x))))

(define (make-move move board)
 (list-replace-ith
  board
  (first move)
  (list-replace-ith
   (list-ref board (first move)) (second move) (player board))))

(define (at board i j) (list-ref (list-ref board i) j))

;;; EVERY-N SOME-N

(define (win board)
 (define (win? player)
  (let ((n (length board)))
   (or
    (some-n (lambda (i) (every-n (lambda (j) (= (at board i j) player)) n)) n)
    (some-n (lambda (j) (every-n (lambda (i) (= (at board i j) player)) n)) n)
    (every-n (lambda (i) (= (at board i i) player)) n)
    (every-n (lambda (i) (= (at board i (- (- n 1) i)) player)) n))))
 (cond ((win? 1) 1)
       ((win? -1) -1)
       (else 0)))

(define (count-n p n)
 (let loop ((i (- n 1)) (c 0))
  (cond ((negative? i) c)
	((p i) (loop (- i 1) (+ c 1)))
	(else (loop (- i 1) c)))))

(define (potential-wins board player)
 (let ((n (length board)))
  (+ (count-n
      (lambda (i) (every-n (lambda (j) (not (= (at board i j) (- player)))) n))
      n)
     (count-n
      (lambda (j) (every-n (lambda (i) (not (= (at board i j) (- player)))) n))
      n)
     (if (every-n (lambda (i) (not (= (at board i i) (- player)))) n) 1 0)
     (if (every-n (lambda (i) (not (= (at board i (- n i 1)) (- player)))) n)
	 1
	 0))))

(define (static-evaluator board)
 (cond ((not (zero? (win board))) (win board))
       ((null? (moves board)) 0)
       (else (/ (- (potential-wins board 1) (potential-wins board -1))
		(+ (* 2 (length board)) 2)))))

(define (maximize f l limit)
 (define (loop best-so-far l)
  (cond ((>= best-so-far limit) 1)
	((null? l) best-so-far)
	(else (loop (max (f (first l) best-so-far) best-so-far) (rest l)))))
 (loop -1 l))

(define (win~-alpha/beta k board limit)
 (cond ((not (zero? (win board))) (win board))
       ((null? (moves board)) 0)
       ((<= k 0) (static-evaluator board))
       (else
	(* (player board)
	   (maximize
	    (lambda (move limit)
	     (* (player board)
		(win~-alpha/beta
		 (- k 1) (make-move move board) (* (player board) limit))))
	    (moves board)
	    (* (player board) limit))))))

(define (win~ k board) (win~-alpha/beta k board (player board)))

(define (optimal-moves~ k board)
 (if (zero? (win board))
     (remove-if-not
      (lambda (move)
       (>= (* (player board) (win~ (- k 1) (make-move move board)))
	   (* (player board) (win~ k board))))
      (moves board))
     '()))
