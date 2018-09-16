#include <stdio.h>
#include <stdlib.h>
#include <lbfgs.h>
#include <math.h>


#ifdef  _MSC_VER
#define inline  __inline
#endif/*_MSC_VER*/
#include <arithmetic_ansi.h>
#include <alm.h>

#define min2(a, b)      ((a) <= (b) ? (a) : (b))
#define max2(a, b)      ((a) >= (b) ? (a) : (b))

void alm_parameter_init( alm_parameter_t* param )
{
    lbfgs_parameter_init(&param->lbfgs_param);
    param->glax_pow = 0.1;
    param->constrain_tol = 1e-8;
    param->glax_tol = 1e-8;
    param->rho = 10;
    param->rho_times = 10;
    param->max_iter = 100;
    param->constrain_powa = 0.1;
    param->constrain_powb = 0.5;
    param->fdiff = 1e-16;
    param->glax_base = 10;
}

static lbfgsfloatval_t xstep(
    void *instance,
    const lbfgsfloatval_t *x,
    lbfgsfloatval_t *g,
    const int n,
    const lbfgsfloatval_t step
    )
{
    alm_instance_t *alm_instance;
    lbfgsfloatval_t fx, lax, *cx_gradient_weight, ycx,wcx;
    int i=0, tmpi_thompson;

    alm_instance = (alm_instance_t*) instance;
    fx = alm_instance->proc_evaluate(alm_instance->custom_instance, x, g, n, step);
    alm_instance->fx = fx;
    vec2norm(&alm_instance->g_norm, g, n);
    alm_instance->cons_evaluate(alm_instance->custom_instance, x, alm_instance->cx, alm_instance->cx_gradient, n, alm_instance->m, 1);
    vecdot(&ycx, alm_instance->y, alm_instance->cx, alm_instance->m);
    lax = fx - ycx;
    
    vec2norm(&alm_instance->cx_norm, alm_instance->cx, alm_instance->m);
    lax += (alm_instance -> rho / 2.0 * alm_instance->cx_norm * alm_instance->cx_norm);
    
    cx_gradient_weight = (lbfgsfloatval_t*)vecalloc(alm_instance->m * sizeof(lbfgsfloatval_t));
    
    for (i=0; i < alm_instance->m; i++)
    {
        cx_gradient_weight[i]= alm_instance->y[i]-alm_instance->rho*alm_instance->cx[i];
    }
    for (i=0; i < n; i++)
    {
        /* general case */
        
        vecdot(&wcx, cx_gradient_weight, &alm_instance->cx_gradient[i*alm_instance->m], alm_instance->m); 
        g[i]=g[i]-wcx;
        
        
        /* optimized for thompson */
        /* tmpi_thompson = i/(n/alm_instance->m);
        wcx = cx_gradient_weight[tmpi_thompson] * alm_instance->cx_gradient[i*alm_instance->m+tmpi_thompson];
        g[i]=g[i]-wcx; */

    }
    vec2norm(&alm_instance->x_norm, x, n);
    vec2norm(&alm_instance->lax_g_norm, g, n);
    vec2norm(&alm_instance->cxg_norm, alm_instance->cx_gradient, n*alm_instance->m);
    vecfree(cx_gradient_weight);
    return lax;
}

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
    )
{
    alm_instance_t * alm_instance;
    int lbfgs_ret, i, ret;
    lbfgsfloatval_t lax;
    lbfgsfloatval_t *g, *xp, *yp, fp; 
    /*lbfgsfloatval_t xnorm;*/
    lbfgsfloatval_t rhok, constrain_tolk, fg_tolk;
    int iter;
    alm_parameter_t *alm_param;

    if ( !param )
    {
        alm_param = (alm_parameter_t *) malloc(sizeof(alm_parameter_t));
        alm_parameter_init(alm_param);
    }
    else
    {
        alm_param = param;
    }

    iter = 1;
    rhok = alm_param->rho;
    fg_tolk = 1.0/rhok;
    constrain_tolk = 1.0/pow(rhok,alm_param->constrain_powa);

    g = (lbfgsfloatval_t *) vecalloc(n*sizeof(lbfgsfloatval_t));
    xp = (lbfgsfloatval_t *) vecalloc(n*sizeof(lbfgsfloatval_t));
    yp = (lbfgsfloatval_t *) vecalloc(m*sizeof(lbfgsfloatval_t));
    fp = 0;
    alm_instance = (alm_instance_t*) malloc(sizeof(alm_instance_t));
    alm_instance->y = (lbfgsfloatval_t*) vecalloc(m*sizeof(lbfgsfloatval_t));
    alm_instance->cx = (lbfgsfloatval_t*) vecalloc(n*sizeof(lbfgsfloatval_t));
    alm_instance->cx_gradient = (lbfgsfloatval_t*) vecalloc(m*n*sizeof(lbfgsfloatval_t));
    alm_instance->rho = rhok;
    alm_instance->proc_evaluate = proc_evaluate;
    alm_instance->cons_evaluate = cons_evaluate;
    alm_instance->m = m;
    alm_instance->custom_instance = instance;
    alm_instance->cx_norm = 0;
    alm_instance->lax_g_norm = 0;
    alm_instance->fx = 0;

    xstep(alm_instance, x, g, n, 0);
    printf("Iter 0: fx = %f \n", alm_instance->fx);
    
    while (iter <= alm_param->max_iter)
    {
        printf("=======ALM Iter %d =================================\n", iter);
        veccpy(xp, x, n);
        veccpy(yp, alm_instance->y, m);
        fp = alm_instance->fx;
        
        /*alm_param->lbfgs_param.epsilon = max2(alm_param->glax_tol,fg_tolk) / xnorm;*/
        alm_param->lbfgs_param.epsilon = max2(alm_param->glax_tol,fg_tolk);
        alm_param->lbfgs_param.gtol = 0.99999;
        /*alm_param->lbfgs_param.wolfe = 0.9999;
        alm_param->lbfgs_param.linesearch = LBFGS_LINESEARCH_BACKTRACKING_WOLFE; */
        alm_param->lbfgs_param.max_linesearch = 50;

        /* find xstep */
        lbfgs_ret = lbfgs(n, x, &lax, xstep, lbfgs_progress, alm_instance, &alm_param->lbfgs_param);
        xstep(alm_instance, x, g, n, 0);

        alm_progress(instance, x, g, alm_instance->fx, alm_instance->x_norm, alm_instance->g_norm, alm_instance->cx_norm, alm_instance->lax_g_norm, max2(alm_instance->fx,fp)-min2(alm_instance->fx,fp), n, m, iter, lbfgs_ret);
        printf("  lbfgs_ret=%d, f= %.2f, xnorm = %.2f, gnorm = %f, cxnorm = %f, rho = %.0f \n", lbfgs_ret, alm_instance->fx, alm_instance->x_norm, alm_instance->lax_g_norm, alm_instance->cx_norm, rhok);
        
        if (alm_instance->cx_norm <= max2(constrain_tolk,alm_param->constrain_tol))
        {
            if ((alm_instance->cx_norm <= alm_param->constrain_tol 
                 && alm_instance->lax_g_norm / alm_instance->x_norm <= alm_param->glax_tol))
            {
                ret = LBFGS_SUCCESS;
                *ptr_fx = alm_instance->fx;
                break;
            }
            if (alm_instance->cx_norm <= alm_param->constrain_tol && max2(alm_instance->fx,fp)-min2(alm_instance->fx,fp) < alm_param->fdiff)
            {                
                ret = LBFGS_STOP;
                *ptr_fx = alm_instance->fx;
                break;
            }
            /* y step */
            for (i=0; i< alm_instance->m; i++)
            {
                alm_instance->y[i]=alm_instance->y[i]-alm_instance->rho*alm_instance->cx[i];
            }
            alm_instance->rho = rhok;
            constrain_tolk = constrain_tolk / pow(alm_instance->rho, alm_param->constrain_powb);
            fg_tolk = fg_tolk/pow(alm_instance->rho,alm_param->glax_pow); 
            /* fg_tolk = alm_param->glax_tol + pow(alm_param->glax_base,-iter); */
            /* fg_tolk = fg_tolk / alm_param->rho_times; */
        }
        else/* if (lbfgs_ret >= 0)*/
        {
            /*veccpy(x, xp, n);
              veccpy(alm_instance->y, yp, m); */
            rhok = alm_param->rho_times*rhok;
            alm_instance->rho = rhok;
            constrain_tolk = 1/ pow(rhok, alm_param->constrain_powa);
            fg_tolk = 1/rhok;
            /* fg_tolk = alm_param->glax_tol + pow(alm_param->glax_base,-iter); */
            /* fg_tolk = 1/alm_param->rho; */
        }
        /*else
        {
            veccpy(x, xp, n);
            veccpy(alm_instance->y, yp, m);
            rhok = alm_param->rho;
            alm_instance->rho = rhok;
            constrain_tolk = 1/ pow(rhok, alm_param->constrain_powb);
            fg_tolk = 1/rhok;
        }*/
        iter++;
    }
    if (iter > alm_param->max_iter)
    {
        ret = LBFGSERR_MAXIMUMITERATION;
        *ptr_fx = alm_instance->fx;
    }

    /* Clean up*/
    if (!param)
        free(alm_param);
    vecfree(alm_instance->y);
    vecfree(alm_instance->cx_gradient);
    vecfree(alm_instance->cx);
    vecfree(g);
    vecfree(xp);
    vecfree(yp);
    free(alm_instance);
    return ret;
}
