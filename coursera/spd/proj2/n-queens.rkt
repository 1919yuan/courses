;; The first three lines of this file were inserted by DrRacket. They record metadata
;; about the language level of this file in a form that our tools can easily process.
#reader(lib "htdp-intermediate-reader.ss" "lang")((modname n-queens) (read-case-sensitive #t) (teachpacks ()) (htdp-settings #(#t constructor repeating-decimal #f #t none #f ())))
(require racket/list)
(define B 0)
(define Q 1)
(define (Q? x)
  (= x Q))
(define (B? x)
  (= x B))
(define SIZE 4)
(define B2 (list B B B B))
(define B4 (list B B B B B B B B B B B B B B B B))
(define INDEXES (build-list (* SIZE SIZE) identity ))
(define (index r c)
  (+ c (* r SIZE)))
(define (row index)
  (quotient index SIZE))
(define (column index)
  (remainder index SIZE))
(define (solve bd)
  (local [(define (solve--bd bd)
            (if (solved? bd)
                (list bd)
                (solve--lobd (next-boards bd))))
          (define (solve--lobd lobd)
            (if (empty? lobd)
                empty
                (append (solve--bd (first lobd))
                      (solve--lobd (rest lobd)))))]
    (solve--bd bd)))

(define (solved? bd)
  (= SIZE (foldr + 0 bd)))

(define (next-boards bd)
  (local [(define c (find-column bd))]
    (if (= c (- SIZE 1))
        empty
        (keep-only-valid (fill-column (+ 1 c) bd)))))

(define (queen-positions bd)
  (local [(define (pos-queen? pos)
            (Q? (list-ref bd pos)))]
    (filter pos-queen? INDEXES)))

(define (find-column bd)
  (foldr max -1 (map column (queen-positions bd))))

(define (find-max-column-pos bd)
  (local [(define positions (queen-positions bd))
          (define c (find-column bd))
          (define (c-match? pos)
            (= c (column pos)))]
    (if (empty? positions)
        -1
        (first (filter c-match? positions)))))

(define (set-val bd p v)
  (append (take bd p)
          (list v)
          (drop bd (add1 p))))

(define (fill-column c bd)
  (local [(define (fill-row i)
            (set-val bd (index i c) Q))]
    (map fill-row (build-list SIZE identity))))

(define (keep-only-valid lobd)
  (filter valid? lobd))

(define (valid? bd)
  (local [(define positions (queen-positions bd))
          (define new-queen-position (find-max-column-pos bd))
          (define (attack-new-queen? p) (attack? p new-queen-position))]
    (not (ormap attack-new-queen? positions))))

(define (attack? pos1 pos2)
  (local [(define c1 (column pos1))
          (define c2 (column pos2))
          (define r1 (row pos1))
          (define r2 (row pos2))]
    (cond
      [(and (= r1 r2) (= c1 c2)) false]
      [(= r1 r2) true]
      [(= c1 c2) true]
      [(= (abs (- r1 r2)) (abs (- c1 c2))) true]
      [else false])))

(solve B4)