(define-structure state stack words)

(define (parse-a-word state category lexicon)
 (let ((words (state-words state)))
  (when (null? words) (fail))
  (unless (memq (first words) lexicon) (fail))
  (make-state (cons (list category (first words)) (state-stack state))
	     (rest words))))

(define (pop-one category state)
 (let ((stack (state-stack state)))
  (make-state (cons (list category (first stack)) (rest stack))
	      (state-words state))))

(define (pop-two category state)
 (let ((stack (state-stack state)))
  (make-state
   (cons (list category (second stack) (first stack)) (rest (rest stack)))
   (state-words state))))

(define (parse-a-common-noun state)
 (parse-a-word state 'n-common '(dog hippopotamus umbrella)))

(define (parse-a-proper-noun state)
 (parse-a-word state 'n-proper '(george paris)))

(define (parse-a-determiner state)
 (parse-a-word state 'det '(a the some)))

(define (parse-a-noun-phrase state)
 (either (pop-one 'np (parse-a-proper-noun state))
	 (pop-two 'np (parse-a-common-noun (parse-a-determiner state)))))

(define (parse-an-intransitive-verb state)
 (parse-a-word state 'v-intrans '(sleeps walks)))

(define (parse-a-transitive-verb state)
 (parse-a-word state 'v-trans '(eats follows)))

(define (parse-a-verb-phrase state)
 (either (pop-one 'vp (parse-an-intransitive-verb state))
	 (pop-two 'vp (parse-a-noun-phrase (parse-a-transitive-verb state)))))

(define (parse-a-sentence state)
 (pop-two 's (parse-a-verb-phrase (parse-a-noun-phrase state))))

(define (a-parse words)
 (let ((state (parse-a-sentence (make-state '() words))))
  (unless (null? (state-words state)) (fail))
  (first (state-stack state))))
