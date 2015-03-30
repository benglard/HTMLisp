# HTMLisp
HTMLisp is a tiny, lisp-inspired HTML templating engine built on Peter Norvig's [Lispy](http://norvig.com/lispy.html).

## Example Usage:
```lisp
(define x 10);
(define y 20);
(html lang=en
    (head
        (link rel=stylesheet src=/main.css)
        (script type=text/javascript src=/main.js)
    )
    (body
        (div
            (p id=doc class=class-name (quote the))
            (p (x))
            (p (y))
        )
    )
);
```