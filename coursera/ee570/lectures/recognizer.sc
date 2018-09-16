(define (strip-a-word words lexicon)
 (when (null? words) (fail))
 (unless (memq (first words) lexicon) (fail))
 (rest words))

(define (strip-a-common-noun words)
 (strip-a-word words '(dog hippopotamus umbrella)))

(define (strip-a-proper-noun words)
 (strip-a-word words '(george paris)))

(define (strip-a-determiner words)
 (strip-a-word words '(a the some)))

(define (strip-a-noun-phrase words)
 (either (strip-a-proper-noun words)
	 (strip-a-common-noun (strip-a-determiner words))))

(define (strip-an-intransitive-verb words)
 (strip-a-word words '(sleeps walks)))

(define (strip-a-transitive-verb words)
 (strip-a-word words '(eats follows)))

(define (strip-a-verb-phrase words)
 (either (strip-an-intransitive-verb words)
	 (strip-a-noun-phrase (strip-a-transitive-verb words))))

(define (strip-a-sentence words)
 (strip-a-verb-phrase (strip-a-noun-phrase words)))

(define (sentence? words)
 (possibly? (null? (strip-a-sentence words))))
