;;;; Mathematical Computations in XTK Lisp DSL
;;;; ==========================================
;;;; This file contains sophisticated mathematical expressions
;;;; and transformations written in the XTK Lisp-like DSL.

;;; ============================================================
;;; CALCULUS AND ANALYSIS
;;; ============================================================

;; Taylor series expansion of e^x around x=0
(taylor-expand (exp x) x 0 5)
;; => (+ 1 x (/ (^ x 2) 2) (/ (^ x 3) 6) (/ (^ x 4) 24) (/ (^ x 5) 120))

;; Partial derivatives for multivariable functions
(∂/∂x (+ (^ x 3) (* 2 x y) (^ y 2)))
;; => (+ (* 3 (^ x 2)) (* 2 y))

(∂/∂y (+ (^ x 3) (* 2 x y) (^ y 2)))
;; => (+ (* 2 x) (* 2 y))

;; Gradient of a scalar field
(grad (* (sin x) (cos y) (exp z)))
;; => (vector (* (cos x) (cos y) (exp z))
;;            (* (- (sin x)) (sin y) (exp z))
;;            (* (sin x) (cos y) (exp z)))

;; Divergence of a vector field
(div (vector (* x y) (^ y 2) (* x z)))
;; => (+ y (* 2 y) x)

;; Curl of a vector field
(curl (vector (^ y 2) (* x z) (- (* x y))))
;; => (vector (- x z) y (- z (* 2 y)))

;; Laplacian
(∇² (+ (^ x 2) (^ y 2) (^ z 2)))
;; => 6

;; Line integral
(line-integral (vector (* y 2) (* x 2)) 
               (parametric (cos t) (sin t))
               0 (* 2 pi))

;; Surface integral
(surface-integral (dot F (cross (∂u r) (∂v r)))
                  u 0 1
                  v 0 (* 2 pi))

;;; ============================================================
;;; DIFFERENTIAL EQUATIONS
;;; ============================================================

;; Solve first-order ODE: dy/dx = -2xy
(solve-ode (= (dd y x) (* (- 2) x y))
           (initial y 0 1))
;; => (* C (exp (- (^ x 2))))

;; Solve second-order ODE: d²y/dx² + 4y = 0
(solve-ode (= (+ (dd (dd y x) x) (* 4 y)) 0)
           (initial y 0 1)
           (initial (dd y x) 0 2))
;; => (+ (* A (cos (* 2 x))) (* B (sin (* 2 x))))

;; Partial differential equation (heat equation)
(solve-pde (= (∂/∂t u) (* α (∇² u)))
           (boundary u 0 0)
           (boundary u L 0)
           (initial u x (sin (/ (* pi x) L))))

;; Wave equation
(solve-pde (= (∂²/∂t² u) (* (^ c 2) (∂²/∂x² u)))
           (initial u x (gaussian x μ σ))
           (initial (∂/∂t u) x 0))

;;; ============================================================
;;; LINEAR ALGEBRA
;;; ============================================================

;; Matrix operations
(matrix-multiply 
  (matrix ((1 2 3)
           (4 5 6)))
  (matrix ((7 8)
           (9 10)
           (11 12))))
;; => (matrix ((58 64)
;;            (139 154)))

;; Determinant
(det (matrix ((a b c)
              (d e f)
              (g h i))))
;; => (- (+ (* a e i) (* b f g) (* c d h))
;;       (+ (* c e g) (* b d i) (* a f h)))

;; Eigenvalues and eigenvectors
(eigenvalues (matrix ((4 -2)
                      (1 1))))
;; => (list 3 2)

(eigenvector (matrix ((4 -2)
                      (1 1))) 
             3)
;; => (vector 2 1)

;; Matrix exponential
(matrix-exp (* t (matrix ((0 -1)
                           (1 0)))))
;; => (matrix (((cos t) (- (sin t)))
;;            ((sin t) (cos t))))

;; Singular value decomposition
(svd (matrix ((1 2)
              (3 4)
              (5 6))))
;; => (list U Σ V*)

;;; ============================================================
;;; NUMBER THEORY
;;; ============================================================

;; Euler's totient function
(totient 12)
;; => 4  ; Numbers coprime to 12: 1, 5, 7, 11

;; Mobius function
(mobius (* 2 3 5))  ; Square-free with 3 prime factors
;; => -1

;; Dirichlet convolution
(dirichlet-conv (lambda n 1) mobius)
;; => (lambda n (if (= n 1) 1 0))  ; Identity function

;; Continued fraction expansion
(continued-fraction (sqrt 2))
;; => (+ 1 (/ 1 (+ 2 (/ 1 (+ 2 (/ 1 (+ 2 ...)))))))

;; Modular arithmetic
(mod-exp 7 256 13)  ; 7^256 mod 13
;; => 9

;; Chinese Remainder Theorem
(crt (list (≡ x 2 (mod 3))
           (≡ x 3 (mod 5))
           (≡ x 2 (mod 7))))
;; => (≡ x 23 (mod 105))

;;; ============================================================
;;; COMPLEX ANALYSIS
;;; ============================================================

;; Complex arithmetic
(* (complex 3 4) (complex 1 2))
;; => (complex -5 10)

;; Complex conjugate
(conj (complex a b))
;; => (complex a (- b))

;; Complex exponential (Euler's formula)
(exp (complex 0 θ))
;; => (complex (cos θ) (sin θ))

;; Cauchy-Riemann equations
(cauchy-riemann (complex (+ (^ x 2) (- (^ y 2))) (* 2 x y)))
;; => true  ; f(z) = z² is holomorphic

;; Residue theorem
(residue (/ 1 (- z a)) a)
;; => 1

;; Contour integral
(contour-integral (/ 1 z) 
                  (circle 0 1)
                  counterclockwise)
;; => (* 2 pi i)

;;; ============================================================
;;; TOPOLOGY AND GEOMETRY
;;; ============================================================

;; Christoffel symbols
(christoffel g i j k)
;; => (/ (+ (∂_j g_ik) (∂_i g_jk) (- (∂_k g_ij))) 2)

;; Riemann curvature tensor
(riemann Γ i j k l)
;; => (+ (∂_k Γ^i_jl) (- (∂_l Γ^i_jk))
;;       (+ (* Γ^i_mk Γ^m_jl) (- (* Γ^i_ml Γ^m_jk))))

;; Geodesic equation
(geodesic-eq (+ (dd (dd x^i) τ) 
                (* Γ^i_jk (dd x^j) (dd x^k)))
              0)

;; Gaussian curvature
(gauss-curvature (surface z (f x y)))
;; => (/ (- (* f_xx f_yy) (^ f_xy 2))
;;       (^ (+ 1 (^ f_x 2) (^ f_y 2)) 2))

;; Euler characteristic
(euler-char (polyhedron V E F))
;; => (- (+ V F) E)  ; V - E + F = 2 for convex polyhedra

;;; ============================================================
;;; FUNCTIONAL ANALYSIS
;;; ============================================================

;; Inner product
(inner-product f g)
;; => (integrate (* (conj f) g) x -∞ ∞)

;; Norm
(norm f)
;; => (sqrt (inner-product f f))

;; Fourier transform
(fourier-transform f)
;; => (lambda k (/ (integrate (* f (exp (* (- i) k x))) x -∞ ∞)
;;                 (sqrt (* 2 pi))))

;; Inverse Fourier transform
(inverse-fourier (fourier-transform f))
;; => f

;; Convolution
(convolve f g)
;; => (lambda x (integrate (* (f τ) (g (- x τ))) τ -∞ ∞))

;; Green's function
(greens-function (+ (∇² G) (δ r r')))
;; => (/ (- 1) (* 4 pi (norm (- r r'))))

;;; ============================================================
;;; PROBABILITY AND STATISTICS
;;; ============================================================

;; Expectation value
(expectation X P)
;; => (sum (* x_i P_i) i)

;; Variance
(variance X)
;; => (- (expectation (^ X 2)) (^ (expectation X) 2))

;; Characteristic function
(char-function X)
;; => (lambda t (expectation (exp (* i t X))))

;; Moment generating function
(mgf X)
;; => (lambda t (expectation (exp (* t X))))

;; Probability distributions
(gaussian x μ σ)
;; => (/ (exp (- (/ (^ (- x μ) 2) (* 2 (^ σ 2)))))
;;       (* σ (sqrt (* 2 pi))))

(poisson k λ)
;; => (/ (* (^ λ k) (exp (- λ))) (factorial k))

;; Bayes' theorem
(bayes P(A|B) P(B) P(A))
;; => (/ (* P(B|A) P(A)) P(B))

;; Maximum likelihood estimation
(mle (likelihood θ data))
;; => (argmax θ (log-likelihood θ data))

;;; ============================================================
;;; OPTIMIZATION
;;; ============================================================

;; Lagrange multipliers
(lagrangian f (list (= g 0) (= h 0)))
;; => (- f (+ (* λ g) (* μ h)))

;; KKT conditions
(kkt-conditions (minimize f)
                (subject-to (≤ g 0) (= h 0)))

;; Gradient descent
(gradient-descent f x₀ α)
;; => (iterate (lambda x (- x (* α (grad f x)))) x₀)

;; Newton's method
(newton f x₀)
;; => (iterate (lambda x (- x (/ (f x) (dd f x)))) x₀)

;; Conjugate gradient
(conjugate-gradient A b x₀)
;; => (solve (= (* A x) b) (initial x x₀))

;;; ============================================================
;;; SYMBOLIC COMPUTATION PATTERNS
;;; ============================================================

;; Pattern matching for integration
(match-integral (integrate (^ x n) x)
                (case (= n -1) (log (abs x)))
                (default (/ (^ x (+ n 1)) (+ n 1))))

;; Rewrite rules for simplification
(rewrite-rule (+ (sin θ)² (cos θ)²) 1)
(rewrite-rule (- (cosh x)² (sinh x)²) 1)
(rewrite-rule (log (exp x)) x)
(rewrite-rule (exp (log x)) x)

;; Proof by induction
(prove-by-induction 
  (proposition (= (sum k 1 n) (/ (* n (+ n 1)) 2)))
  (base-case n 1)
  (inductive-step (assume n) (prove (+ n 1))))

;; Symbolic limits
(limit (/ (sin x) x) x 0)
;; => 1

(limit (^ (+ 1 (/ 1 n)) n) n ∞)
;; => e

;; Series convergence tests
(ratio-test (/ 1 (factorial n)))
;; => converges

(integral-test (/ 1 (^ n 2)))
;; => converges

;;; ============================================================
;;; END OF MATHEMATICAL COMPUTATIONS
;;; ============================================================