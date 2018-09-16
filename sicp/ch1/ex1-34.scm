;; Calling (f f) will eventually invoke "2" as a procedure, which results in
;; an error.

(define (f g)
  (g 2))
