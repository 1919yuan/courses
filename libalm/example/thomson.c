/* Solves the Thomson problem with n points, and d dimensions, which are the */
/* First 2 command line arguments. */
/* e.g. ./thomson n d */

#include <lbfgs.h>
#include <math.h>
#ifdef  _MSC_VER
#define inline  __inline
#endif/*_MSC_VER*/
#include <arithmetic_ansi.h>
#include <alm.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/timeb.h>
#include <string.h>

struct thompson_instance{
    int m;
    int scale;
    lbfgsfloatval_t* norm_dist;
    lbfgsfloatval_t* tmpdiff;
    FILE* res_file;
    lbfgsfloatval_t gnorm;
    lbfgsfloatval_t cnorm;
    lbfgsfloatval_t xnorm;
    lbfgsfloatval_t laxgnorm;
    lbfgsfloatval_t fdiff;
    lbfgsfloatval_t avg_fx;
};

static lbfgsfloatval_t thompson_function(
    void *instance,
    const lbfgsfloatval_t *x,
    lbfgsfloatval_t *g,
    const int n,
    const lbfgsfloatval_t step
    )
{
    struct thompson_instance* t_ins;
    int i=0,j=0,index=0,m,dim,npts,k=0;
    lbfgsfloatval_t * tmpdiff, *norm_dist, *cur_gi;
    lbfgsfloatval_t fx; /*, tmpg;*/
    t_ins = (struct thompson_instance*) instance;
    norm_dist = t_ins->norm_dist;
    tmpdiff = t_ins->tmpdiff;
    m = t_ins->m;
    dim = n/m;
    npts = m;
    fx = 0;
    vecset(g,0,n);

    for (i=0; i<npts-1; i++)
        for (j=i+1; j<npts; j++)
        {
            vecdiff(tmpdiff, &x[j*dim], &x[i*dim], dim);
            vecdot(&norm_dist[index], tmpdiff, tmpdiff, dim);
            fx += 1/norm_dist[index];
            /*for (k=0; k<dim; k++)
            {
                tmpg = 2*(x[j*dim+k]-x[i*dim+k])/norm_dist[index]/norm_dist[index];
                g[i*dim+k]+=tmpg;
                g[j*dim+k]+=tmpg;
            }*/
            ++index;
        }
    
    for (i=0; i<npts; i++)
    {
        cur_gi = &g[i*dim];
        for (j=0; j<npts; j++)
        {
            if (j>i)
            {
                index = npts*i-(i+1)*i/2+j-i-1;
                for (k=0;k<dim;k++)
                    *(cur_gi+k)=*(cur_gi+k)+2*(x[j*dim+k]-x[i*dim+k])/norm_dist[index]/norm_dist[index];
            }
            else if (j<i)
            {
                index = npts*j-(j+1)*j/2+i-j-1;
                for (k=0;k<dim;k++)
                    *(cur_gi+k)=*(cur_gi+k)+2*(x[j*dim+k]-x[i*dim+k])/norm_dist[index]/norm_dist[index];
            }
        }
    }

    if (t_ins->scale)
    {
        fx = 2 * fx / (npts) / (npts-1);
        vecscale(g, 2.0/npts/(npts-1), n);
    }

    return fx;
}

static void sphere_constraint(
    void *instance,
    const lbfgsfloatval_t *x,
    lbfgsfloatval_t *cx,
    lbfgsfloatval_t *cxg,
    const int n,
    const int m,
    const int bool_gradient
    )
{
    int dim,i,j;
    lbfgsfloatval_t norm_x;
    
    dim = n/m;
    if (bool_gradient)
        vecset(cxg, 0, n*m);
    for (i=0; i<m; i++)
    {
        vecdot(&norm_x, x+i*dim, x+i*dim, dim);
        cx[i] = norm_x - 1;
        if (bool_gradient)
        {
            for (j=0; j<dim; j++)
                cxg[(i*dim+j)*m+i]=2*x[i*dim+j];
        }
    }
}

static int progress_lbfgs(
    void *instance,
    const lbfgsfloatval_t *x,
    const lbfgsfloatval_t *g,
    const lbfgsfloatval_t fx,
    const lbfgsfloatval_t xnorm,
    const lbfgsfloatval_t gnorm,
    const lbfgsfloatval_t step,
    int n,
    int k,
    int ls
    )
{
/*    int i=0;

    alm_instance_t *t_ins= (alm_instance_t*) instance;
    printf("Iteration %d:\n", k);
    printf("  fx = %f, x[0] = %f, x[1] = %f\n", fx, x[0], x[1]);
    printf("  xnorm = %f, gnorm = %f, step = %f, cxnorm = %f\n", xnorm, gnorm, step, t_ins->cx_norm);
    printf("  y = ");
    for (i=0; i<t_ins->m; i++)
    {
        printf("%f\t", t_ins->y[i]);
    }
    printf("\n");
    printf("\n"); */
    return 0;
}

static int progress_alm(
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
    )
{
    int i=0;
    struct thompson_instance* t_ins = (struct thompson_instance*) instance;
    FILE *res_file= t_ins->res_file;
    fprintf(res_file, "%d %e %e %f %f\n", k, gnorm, cnorm, fx, 2*fx/m/(m-1));
    t_ins->gnorm = gnorm;
    t_ins->cnorm = cnorm;
    t_ins->xnorm = xnorm;
    t_ins->laxgnorm = laxgnorm;
    t_ins->avg_fx = 2*fx/m/(m-1);
    t_ins->fdiff = fdiff;
    return 0;
}

int main (int argc, char** argv)
{

    int npts = 3;
    int dim = 3;

    int n;
    int m;
    lbfgsfloatval_t *x,fx,xn;
    alm_parameter_t param;
    int ret;
    struct thompson_instance * t_ins;
    int i=0,j=0;
    lbfgsfloatval_t sumx = 0;
    struct timeb start_time, end_time;
    char filepath[40]="./";
    char res_filename[50]="";
    char x_filename[50]="";
    char tmp[80]="";
    FILE *res_file=0, *x_file=0;

    alm_parameter_init(&param);
    if (argc >= 2 && strcmp(argv[1], "--scale"))
        npts = atoi(argv[1]);
    if (argc >= 3 && strcmp(argv[2], "--scale"))
        dim = atoi(argv[2]);
    if (argc >= 4 && strcmp(argv[3], "--scale"))
        param.rho_times = atof(argv[3]);
    if (argc >= 5 && strcmp(argv[4], "--scale"))
        param.rho = atof(argv[4]);
    if (argc >= 6 && strcmp(argv[5], "--scale"))
        param.constrain_powa = atof(argv[5]);
    if (argc >= 7 && strcmp(argv[6], "--scale"))
        param.constrain_powb = atof(argv[6]);
    if (argc >= 8 && strcmp(argv[7], "--scale"))
        strcpy(filepath, argv[7]);

    param.max_iter = 100;

    sprintf(tmp, "result_alm_%d_%d_%.2lf_%.2lf_%.1lf_%.2lf.txt", npts, dim,param.rho_times,param.rho,param.constrain_powa,param.constrain_powb);
    strcat(res_filename, filepath);
    strcat(res_filename, tmp);
    tmp[0]='\0';
    sprintf(tmp, "x_alm_%d_%d_%.2lf_%.2lf_%.1lf_%.2lf.txt", npts, dim,param.rho_times,param.rho,param.constrain_powa,param.constrain_powb);
    strcat(x_filename, filepath);
    strcat(x_filename, tmp);
    res_file = fopen(res_filename, "w");
    x_file = fopen(x_filename, "w");

    if (!res_file || !x_file) {printf("Cannot open output files for writing results\n"); exit(1);}

    n = npts * dim;
    m = npts;
    x = (lbfgsfloatval_t*) vecalloc(n*sizeof(lbfgsfloatval_t));

    srand(1);
    for (i=0; i<npts; i++)
    {
        sumx=0;
        for (j=0; j<dim; j++)
        {
            x[i*dim+j]=rand()%1000-500;
            sumx+=x[i*dim+j]*x[i*dim+j];
        }
        sumx = sqrt(sumx);
        for (j=0; j<dim; j++)
        {
            x[i*dim+j]/=sumx;
        }
    }
    
    t_ins = (struct thompson_instance*) malloc(sizeof(struct thompson_instance));
    t_ins->m = m;
    t_ins->norm_dist = (lbfgsfloatval_t *) vecalloc(npts * (npts-1) /2*sizeof(lbfgsfloatval_t));
    t_ins->tmpdiff = (lbfgsfloatval_t *) vecalloc(dim*sizeof(lbfgsfloatval_t));
    t_ins->res_file = res_file;
    t_ins->scale = 0;
    for (i=1; i<=argc-1; i++)
        if (!strcmp(argv[i],"--scale"))
            t_ins->scale = 1;

    ftime(&start_time);
    ret=alm(n,m,x,&fx,thompson_function, sphere_constraint, progress_lbfgs, progress_alm, t_ins, &param);
    ftime(&end_time);

    for (i=0; i<npts; i++)
    {
        for (j=0; j<dim; j++)
        {
            fprintf(x_file, "%f ",x[i*dim+j]); 
        }
        vec2norm(&xn,&x[i*dim],dim);
        fprintf(x_file,"%e", xn);
        fprintf(x_file, "\n");
    }
    fprintf(res_file, "Finish with converge flag %d\n", ret);
    /*printf("Finish with converge flag %d\n", ret);
    printf("Final Thompson function value: %f \n", fx);
    printf("Time consumed: %f s.\n", (double)(end_time.time*1000+end_time.millitm-start_time.time*1000+end_time.millitm)/1000);*/
    fprintf(res_file, "%f %e %e %f %e %e\n", (double)(end_time.time*1000+end_time.millitm-start_time.time*1000+end_time.millitm)/1000, t_ins->laxgnorm, t_ins->cnorm/sqrt((double)npts), fx, t_ins->gnorm, t_ins->fdiff);

    fclose(res_file);
    fclose(x_file);
    vecfree(x);
    vecfree(t_ins->tmpdiff);
    vecfree(t_ins->norm_dist);
    free(t_ins);
}
