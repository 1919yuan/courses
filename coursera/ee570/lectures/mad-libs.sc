(define (a-common-noun) (either '(dog) '(hippopotamus) '(umbrella)))

(define (a-proper-noun) (either '(george) '(paris)))

;;; NP -> Nprop
;;;    |  DET Ncommon
;;; DET -> a the some
;;; VP -> Vintrans
;;;    |  Vtrans NP
;;; S -> NP VP

(define (a-determiner) (either '(a) '(the) '(some)))

(define (a-noun-phrase)
 (either (a-proper-noun)
	 (append (a-determiner) (a-common-noun))))

(define (an-intransitive-verb) (either '(sleeps) '(walks)))

(define (a-transitive-verb) (either '(eats) '(follows)))

(define (a-verb-phrase)
 (either (an-intransitive-verb)
	 (append (a-transitive-verb) (a-noun-phrase))))

(define (a-sentence) (append (a-noun-phrase) (a-verb-phrase)))

(define (print-sentences)
 (for-effects
  (write (a-sentence))
  (newline)))
