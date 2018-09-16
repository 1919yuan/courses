(define (lower-left placed-rectangle)
 (placed-rectangle-point placed-rectangle))

(define (lower-right placed-rectangle)
 (v+ (placed-rectangle-point placed-rectangle)
     (vector (rectangle-width (placed-rectangle-rectangle placed-rectangle))
	     0)))

(define (upper-left placed-rectangle)
 (v+ (placed-rectangle-point placed-rectangle)
     (vector
      0 (rectangle-height (placed-rectangle-rectangle placed-rectangle)))))

(define (upper-right placed-rectangle)
 (v+ (placed-rectangle-point placed-rectangle)
     (vector
      (rectangle-width (placed-rectangle-rectangle placed-rectangle))
      (rectangle-height (placed-rectangle-rectangle placed-rectangle)))))

(define (overlaps? placed-rectangle1 placed-rectangle2)
 (not (or (>= (x (lower-left placed-rectangle1))
	      (x (lower-right placed-rectangle2)))
	  (>= (x (lower-left placed-rectangle2))
	      (x (lower-right placed-rectangle1)))
	  (>= (y (lower-left placed-rectangle1))
	      (y (upper-left placed-rectangle2)))
	  (>= (y (lower-left placed-rectangle2))
	      (y (upper-left placed-rectangle1))))))

(define (rotate rectangle)
 (make-rectangle (rectangle-height rectangle) (rectangle-width rectangle)))

(define (place-lower-left rectangle point)
 (make-placed-rectangle rectangle point))

(define (place-lower-right rectangle point)
 (make-placed-rectangle
  rectangle (v- point (vector (rectangle-width rectangle) 0))))

(define (place-upper-left rectangle point)
 (make-placed-rectangle
  rectangle (v- point (vector 0 (rectangle-height rectangle)))))

(define (place-upper-right rectangle point)
 (make-placed-rectangle
  rectangle
  (v- point
      (vector (rectangle-width rectangle) (rectangle-height rectangle)))))

(define (a-rectangle-placement rectangles best-area)
 (if (null? rectangles)
     '()
     (let* ((rectangle (first rectangles))
	    (new-placed-rectangle (place-lower-left rectangle (vector 0 0))))
      (define (loop rectangles placed-rectangles)
       (if (null? rectangles)
	   placed-rectangles
	   (let* ((rectangle (a-member-of rectangles))
		  (new-placed-rectangle
		   ((either place-lower-left
			    place-lower-right
			    place-upper-left
			    place-upper-right)
		    ((either identity rotate) rectangle)
		    ((either lower-left lower-right upper-left upper-right)
		     (a-member-of placed-rectangles)))))
	    (when (some (lambda (placed-rectangle)
			 (overlaps? placed-rectangle new-placed-rectangle))
			placed-rectangles)
	     (fail))
	    (when (>= (area-of-bounding-box
		       (cons new-placed-rectangle placed-rectangles))
		      (best-area))
	     (fail))
	    (place-rectangle! new-placed-rectangle)
	    (loop (removeq rectangle rectangles)
		  (cons new-placed-rectangle placed-rectangles)))))
      (place-rectangle! new-placed-rectangle)
      (loop (rest rectangles) (list new-placed-rectangle)))))

(define (area-of-bounding-box placed-rectangles)
 (let ((min-x (reduce min (map x (map lower-left placed-rectangles)) infinity))
       (min-y (reduce min (map y (map lower-left placed-rectangles)) infinity))
       (max-x (reduce
	       max (map x (map upper-right placed-rectangles)) minus-infinity))
       (max-y
	(reduce
	 max (map y (map upper-right placed-rectangles)) minus-infinity)))
  (* (- max-x min-x) (- max-y min-y))))

(define (best-placement rectangles)
 (let ((best-placement #f))
  (for-effects (let ((placed-rectangles
		      (a-rectangle-placement
		       rectangles
		       (lambda ()
			(if best-placement
			    (area-of-bounding-box best-placement)
			    infinity)))))
		(when (or (not best-placement)
			  (< (area-of-bounding-box placed-rectangles)
			     (area-of-bounding-box best-placement)))
		 (set! best-placement placed-rectangles))))
  best-placement))

;;; 1889 1905 1809
;;;   37   28   43
