#include "code_objects/ring_neurons_stateupdater_codeobject_3.h"
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
        
    inline double _randn(const int _vectorisation_idx) {
        return brian::_random_generators[0].randn();
    }
    static inline int64_t _timestep(double t, double dt)
    {
        return (int64_t)((t + 1e-3*dt)/dt);
    }
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



void _run_ring_neurons_stateupdater_codeobject_3()
{
    using namespace brian;


    ///// CONSTANTS ///////////
    const size_t _numI_ext = 120;
const size_t _numI_syn = 120;
const size_t _numI_vel = 120;
const int64_t N = 120;
const size_t _numV = 120;
const size_t _numdt = 1;
const size_t _numlastspike = 120;
const double msecond = 0.001;
const double mvolt = 0.001;
const size_t _numnot_refractory = 120;
const size_t _numt = 1;
const double uvolt = 1e-06;
    ///// POINTERS ////////////
        
    double* __restrict  _ptr_array_ring_neurons_I_ext = _array_ring_neurons_I_ext;
    double* __restrict  _ptr_array_ring_neurons_I_syn = _array_ring_neurons_I_syn;
    double* __restrict  _ptr_array_ring_neurons_I_vel = _array_ring_neurons_I_vel;
    double* __restrict  _ptr_array_ring_neurons_V = _array_ring_neurons_V;
    double*   _ptr_array_defaultclock_dt = _array_defaultclock_dt;
    double* __restrict  _ptr_array_ring_neurons_lastspike = _array_ring_neurons_lastspike;
    char* __restrict  _ptr_array_ring_neurons_not_refractory = _array_ring_neurons_not_refractory;
    double*   _ptr_array_defaultclock_t = _array_defaultclock_t;


    //// MAIN CODE ////////////
    // scalar code
    const size_t _vectorisation_idx = -1;
        
    const double dt = _ptr_array_defaultclock_dt[0];
    const double t = _ptr_array_defaultclock_t[0];
    const int64_t _lio_1 = _timestep(0.005, dt);
    const double _lio_2 = _brian_pow(dt, 0.5);
    const double _lio_3 = 1.0f*0.1/msecond;
    const double _lio_4 = 1.0f*(7.0 * mvolt)/msecond;
    const double _lio_5 = 1.0f*(31.6227766016838 * uvolt)/(_brian_pow(msecond, 0.5));
    const double _lio_6 = 0.0 - _lio_4;


    const int _N = N;
    
    for(int _idx=0; _idx<_N; _idx++)
    {
        // vector code
        const size_t _vectorisation_idx = _idx;
                
        const double I_ext = _ptr_array_ring_neurons_I_ext[_idx];
        const double I_syn = _ptr_array_ring_neurons_I_syn[_idx];
        const double I_vel = _ptr_array_ring_neurons_I_vel[_idx];
        double V = _ptr_array_ring_neurons_V[_idx];
        const double lastspike = _ptr_array_ring_neurons_lastspike[_idx];
        char not_refractory = _ptr_array_ring_neurons_not_refractory[_idx];
        not_refractory = _timestep(t - lastspike, dt) >= _lio_1;
        const double xi = _lio_2 * _randn(_vectorisation_idx);
        double _V;
        if(!not_refractory)
            _V = V;
        else 
            _V = (V + (dt * ((_lio_6 + (((_lio_3 * I_ext) + (_lio_3 * I_syn)) + (_lio_3 * I_vel))) - (_lio_3 * V)))) + (_lio_5 * xi);
        if(not_refractory)
            V = _V;
        _ptr_array_ring_neurons_V[_idx] = V;
        _ptr_array_ring_neurons_not_refractory[_idx] = not_refractory;

    }

}


