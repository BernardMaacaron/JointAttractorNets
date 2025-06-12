#include "code_objects/ring_synapses_asym_group_variable_set_conditional_codeobject.h"
#include "objects.h"
#include "brianlib/common_math.h"
#include "brianlib/stdint_compat.h"
#include<cmath>
#include<ctime>
#include<iostream>
#include<fstream>
#include<climits>

////// SUPPORT CODE ///////
namespace {
        
    template < typename T1, typename T2 > struct _higher_type;
    template < > struct _higher_type<int32_t,int32_t> { typedef int32_t type; };
    template < > struct _higher_type<int32_t,int64_t> { typedef int64_t type; };
    template < > struct _higher_type<int32_t,float> { typedef float type; };
    template < > struct _higher_type<int32_t,double> { typedef double type; };
    template < > struct _higher_type<int32_t,long double> { typedef long double type; };
    template < > struct _higher_type<int64_t,int32_t> { typedef int64_t type; };
    template < > struct _higher_type<int64_t,int64_t> { typedef int64_t type; };
    template < > struct _higher_type<int64_t,float> { typedef float type; };
    template < > struct _higher_type<int64_t,double> { typedef double type; };
    template < > struct _higher_type<int64_t,long double> { typedef long double type; };
    template < > struct _higher_type<float,int32_t> { typedef float type; };
    template < > struct _higher_type<float,int64_t> { typedef float type; };
    template < > struct _higher_type<float,float> { typedef float type; };
    template < > struct _higher_type<float,double> { typedef double type; };
    template < > struct _higher_type<float,long double> { typedef long double type; };
    template < > struct _higher_type<double,int32_t> { typedef double type; };
    template < > struct _higher_type<double,int64_t> { typedef double type; };
    template < > struct _higher_type<double,float> { typedef double type; };
    template < > struct _higher_type<double,double> { typedef double type; };
    template < > struct _higher_type<double,long double> { typedef long double type; };
    template < > struct _higher_type<long double,int32_t> { typedef long double type; };
    template < > struct _higher_type<long double,int64_t> { typedef long double type; };
    template < > struct _higher_type<long double,float> { typedef long double type; };
    template < > struct _higher_type<long double,double> { typedef long double type; };
    template < > struct _higher_type<long double,long double> { typedef long double type; };
    // General template, used for floating point types
    template < typename T1, typename T2 >
    static inline typename _higher_type<T1,T2>::type
    _brian_mod(T1 x, T2 y)
    {
        return x-y*floor(1.0*x/y);
    }
    // Specific implementations for integer types
    // (from Cython, see LICENSE file)
    template <>
    inline int32_t _brian_mod(int32_t x, int32_t y)
    {
        int32_t r = x % y;
        r += ((r != 0) & ((r ^ y) < 0)) * y;
        return r;
    }
    template <>
    inline int64_t _brian_mod(int32_t x, int64_t y)
    {
        int64_t r = x % y;
        r += ((r != 0) & ((r ^ y) < 0)) * y;
        return r;
    }
    template <>
    inline int64_t _brian_mod(int64_t x, int32_t y)
    {
        int64_t r = x % y;
        r += ((r != 0) & ((r ^ y) < 0)) * y;
        return r;
    }
    template <>
    inline int64_t _brian_mod(int64_t x, int64_t y)
    {
        int64_t r = x % y;
        r += ((r != 0) & ((r ^ y) < 0)) * y;
        return r;
    }
    // General implementation, used for floating point types
    template < typename T1, typename T2 >
    static inline typename _higher_type<T1,T2>::type
    _brian_floordiv(T1 x, T2 y)
    {{
        return floor(1.0*x/y);
    }}
    // Specific implementations for integer types
    // (from Cython, see LICENSE file)
    template <>
    inline int32_t _brian_floordiv<int32_t, int32_t>(int32_t a, int32_t b) {
        int32_t q = a / b;
        int32_t r = a - q*b;
        q -= ((r != 0) & ((r ^ b) < 0));
        return q;
    }
    template <>
    inline int64_t _brian_floordiv<int32_t, int64_t>(int32_t a, int64_t b) {
        int64_t q = a / b;
        int64_t r = a - q*b;
        q -= ((r != 0) & ((r ^ b) < 0));
        return q;
    }
    template <>
    inline int64_t _brian_floordiv<int64_t, int>(int64_t a, int32_t b) {
        int64_t q = a / b;
        int64_t r = a - q*b;
        q -= ((r != 0) & ((r ^ b) < 0));
        return q;
    }
    template <>
    inline int64_t _brian_floordiv<int64_t, int64_t>(int64_t a, int64_t b) {
        int64_t q = a / b;
        int64_t r = a - q*b;
        q -= ((r != 0) & ((r ^ b) < 0));
        return q;
    }
    #ifdef _MSC_VER
    #define _brian_pow(x, y) (pow((double)(x), (y)))
    #else
    #define _brian_pow(x, y) (pow((x), (y)))
    #endif

}

////// HASH DEFINES ///////



void _run_ring_synapses_asym_group_variable_set_conditional_codeobject()
{
    using namespace brian;


    ///// CONSTANTS ///////////
    const size_t _numN = 1;
const int64_t _theta_post_ring_neurons_N = 120;
const size_t _num_theta_post_ring_neurons_i = 120;
const int64_t _theta_pre_ring_neurons_N = 120;
const size_t _num_theta_pre_ring_neurons_i = 120;
const double g_sine = 0.0001;
const double pi = 3.141592653589793;
double* const _array_ring_synapses_asym_w_asym = _dynamic_array_ring_synapses_asym_w_asym.empty()? 0 : &_dynamic_array_ring_synapses_asym_w_asym[0];
const size_t _numw_asym = _dynamic_array_ring_synapses_asym_w_asym.size();
int32_t* const _array_ring_synapses_asym__synaptic_post = _dynamic_array_ring_synapses_asym__synaptic_post.empty()? 0 : &_dynamic_array_ring_synapses_asym__synaptic_post[0];
const size_t _num_postsynaptic_idx = _dynamic_array_ring_synapses_asym__synaptic_post.size();
int32_t* const _array_ring_synapses_asym__synaptic_pre = _dynamic_array_ring_synapses_asym__synaptic_pre.empty()? 0 : &_dynamic_array_ring_synapses_asym__synaptic_pre[0];
const size_t _num_presynaptic_idx = _dynamic_array_ring_synapses_asym__synaptic_pre.size();
    ///// POINTERS ////////////
        
    int32_t*   _ptr_array_ring_synapses_asym_N = _array_ring_synapses_asym_N;
    int32_t* __restrict  _ptr_array_ring_neurons_i = _array_ring_neurons_i;
    double* __restrict  _ptr_array_ring_synapses_asym_w_asym = _array_ring_synapses_asym_w_asym;
    int32_t* __restrict  _ptr_array_ring_synapses_asym__synaptic_post = _array_ring_synapses_asym__synaptic_post;
    int32_t* __restrict  _ptr_array_ring_synapses_asym__synaptic_pre = _array_ring_synapses_asym__synaptic_pre;


//// MAIN CODE ////////////
// scalar code
const size_t _vectorisation_idx = -1;



const double _lio_statement_1 = 1.0f*6.283185307179586/_theta_post_ring_neurons_N;
const double _lio_statement_2 = 1.0f*6.283185307179586/_theta_pre_ring_neurons_N;


const int _N = _array_ring_synapses_asym_N[0];


for(int _idx=0; _idx<_N; _idx++)
{
    // vector code
    const size_t _vectorisation_idx = _idx;
        
    const char _cond = true;

    if (_cond)
    {
                
        const int32_t _postsynaptic_idx = _ptr_array_ring_synapses_asym__synaptic_post[_idx];
        const int32_t _presynaptic_idx = _ptr_array_ring_synapses_asym__synaptic_pre[_idx];
        const int32_t _theta_post_ring_neurons_i = _ptr_array_ring_neurons_i[_postsynaptic_idx];
        const int32_t _theta_pre_ring_neurons_i = _ptr_array_ring_neurons_i[_presynaptic_idx];
        double w_asym;
        const double theta_post = _lio_statement_1 * _theta_post_ring_neurons_i;
        const double theta_pre = _lio_statement_2 * _theta_pre_ring_neurons_i;
        w_asym = g_sine * sin(theta_pre - theta_post);
        _ptr_array_ring_synapses_asym_w_asym[_idx] = w_asym;

    }
}

}


