#ifndef __alm_h__
#define __alm_h__

#include <lbfgs.h>
#include <math.h>

#ifdef  __cplusplus
extern "C" {
#endif/*__cplusplus*/

typedef void (*lbfgs_constrain_t)(
    void *instance,
    const lbfgsfloatval_t *x,
    lbfgsfloatval_t *cx,
    lbfgsfloatval_t *cxg,
    const int n,
    const int m,
    const int bool_gradient
    );

typedef int (*alm_progress_t)(
    void *instance,
    const lbfgsfloatval_t *x,
    const lbfgsfloatval_t *g,
    const lbfgsfloatval_t fx,
    const lbfgsfloatval_t xnorm,
    const lbfgsfloatval_t gnorm,
    const lbfgsfloatval_t cnorm,
    const lbfgsfloatval_t laxgnorm,
    const lbfgsfloatval_t fdiff,
    int n,
    int m,
    int k,
    int ls
    );

typedef struct alm_instance_t{
    lbfgsfloatval_t *y;
    lbfgsfloatval_t *cx_gradient;
    lbfgsfloatval_t *cx;
    lbfgsfloatval_t rho;
    lbfgsfloatval_t lax_g_norm;
    lbfgsfloatval_t x_norm;
    lbfgsfloatval_t cx_norm;
    lbfgsfloatval_t g_norm;
    lbfgsfloatval_t cxg_norm;
    lbfgs_evaluate_t proc_evaluate;
    lbfgs_constrain_t cons_evaluate;
    int m;
    void* custom_instance;
    lbfgsfloatval_t fx;
} alm_instance_t;

typedef struct alm_parameter_t {
    lbfgs_parameter_t lbfgs_param;
    lbfgsfloatval_t rho;
    lbfgsfloatval_t rho_times;
    lbfgsfloatval_t constrain_tol;
    lbfgsfloatval_t glax_tol;
    lbfgsfloatval_t glax_pow;
    int max_iter;
    lbfgsfloatval_t constrain_powa;
    lbfgsfloatval_t constrain_powb;
    lbfgsfloatval_t fdiff;
    lbfgsfloatval_t glax_base;
} alm_parameter_t;

void alm_parameter_init( alm_parameter_t* param );

int alm(
    int n,
    int m,
    lbfgsfloatval_t *x,
    lbfgsfloatval_t *ptr_fx,
    lbfgs_evaluate_t proc_evaluate,
    lbfgs_constrain_t cons_evaluate,
    lbfgs_progress_t lbfgs_progress,
    alm_progress_t alm_progress,
    void *instance,
    alm_parameter_t *param
    );

#ifdef  __cplusplus
}
#endif/*__cplusplus*/

#endif
