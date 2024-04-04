#ifndef _TARGETCTL_ICE
#define _TARGETCTL_ICE


#include <tcd_ice_base.ice>


[["python:pkgdir:TcdIce_gen"]]
module TcdIce {

    // Targets management

    module TargetCtl {

        enum error_t {
            E_SUCCESS,
            E_STDEXC,     // std::exception
            E_UNKEXC,     // unknown exception
            E_BADARG,     // bad argument
        };

        exception TargetCtlError extends BaseException {
            error_t errcode;
        };

        sequence<int> int_seq;
        sequence<double> double_seq;
        sequence<string> string_seq;
        sequence<bool> bool_seq;
        dictionary<string, string> str_str_map;

        struct targetinfo_t {
            string targetspec;
            string source_ref;
            string textname;
            str_str_map catrefs;

            int meas_count;    // number of measurements from the selected source
            double meas_mjd;   // epoch of the last measurement
            string meas_src;   // the selected source of measurements

            double orbit_mjd;  // epoch of the orbit

            // xyzpos data ranges (all sequences are of the same length)
            double_seq xyzpos_mjd1;  // first epoch for every range
            double_seq xyzpos_mjd2;  // last epoch for every range
            int_seq xyzpos_npoints;  // number of points for every range
        };
        sequence<targetinfo_t> targetinfo_seq;

        struct meas_data_t {
            string target;
            string source;
            double_seq mjd;  // [days] Modified JD, UTC
            double_seq x0;   // [radians] e.g. RA (ICRS), H.A. (apparent), Azimuth, etc
            double_seq x1;   // [radians] e.g. DEC (ICRS), DEC (apparent), Elevation, etc
        };
        sequence<meas_data_t> meas_data_seq;

        struct orbit_params_t {
            double t0;         // [mjd] epoch of elements, UTC
            double a;          // [km] semi-major axis
            double ecc;        // eccentricity
            double incl;       // [radians] inclination
            double raan;       // [radians] right ascension of ascending node
            double argp;       // [radians] argument of perigee
            double anmean;     // [radians] mean anomaly
            string system;     // type of orbital elements ('TEME', 'TOD')
            string propagator; // orbit propagator ('kepler', 'sgp4', ...)
            double bstar = 0.; // (SGP4) drag term (aka radiation pressure coefficient)
            double mu = 0.;    // standard gravitational parameter (mu=GM)
        };

        struct use_orbit_t {
            string target;
            string catalog;
            orbit_params_t orbit;
            string source_ref;
            string textname;
            str_str_map catrefs;
        };
        sequence<use_orbit_t> use_orbit_seq;

        struct use_xyzpos_t {
            string target;
            string catalog;
            string source_ref;
            string textname;
            str_str_map catrefs;

            double_seq mjd;
            double_seq x;
            double_seq y;
            double_seq z;
            double_seq vx;
            double_seq vy;
            double_seq vz;
        };
        sequence<use_xyzpos_t> use_xyzpos_seq;

        struct set_magnitude_t {
            string target;
            string catalog;
            double mag0;  // standard magnitude at 1000km and 90deg phase angle
        };
        sequence<set_magnitude_t> set_magnitude_seq;

        interface TargetServ {
            // Update measurement points for some (possible new) target:
            // 1. delete previously added points from the range [mjd1, mjd2].
            // 2. add new points (add_(mjd|x0|x1) must have the same length).
            void update_meas_points(string target, string source,
                double delete_mjd1, double delete_mjd2,
                double_seq add_mjd, double_seq add_x0, double_seq add_x1)
                throws TargetCtlError;

            // Upload orbital elements for a number of targets.
            idempotent void use_orbits(use_orbit_seq orbits);

            // Upload xyz-points for a number of targets.
            idempotent void use_xyzpos(use_xyzpos_seq records);

            // Set magnitudes for previously registered targets.
            idempotent void set_magnitudes(set_magnitude_seq records);

            // Get measurement points for the given range [mjd1, mjd2]. Limit to
            // the given target and/or source (if not empty strings). Return empty
            // sequence if no data.
            idempotent meas_data_seq get_meas_points(string target, string source,
                double mjd1, double mjd2) throws TargetCtlError;

            // Get targets information. Return empty sequence if no data.
            idempotent targetinfo_seq get_targets(string_seq targetspecs) throws TargetCtlError;

            // Query catalog for targets for the given range [mjd1, mjd2]. Return empty
            // sequence if no data.
            idempotent targetinfo_seq filter_catalog(string catalog, double mjd1, double mjd2)
                throws TargetCtlError;

            // Get ephemerides for the given range [mjd1, mjd2]. Limit to the given
            // target and/or source (if not empty strings). Return empty sequence if
            // no data.
            // The length of output ephemeris can be less than requested npoints in
            // some cases (e.g. there will be only one point for fixed sky objects
            // like stars).
            idempotent meas_data_seq get_ephems(string target, string source,
                double mjd1, double mjd2, int npoints) throws TargetCtlError;

            // Delete targets. Limit to the given target and/or source (if not empty
            // strings). Return the number of deleted [target, source] pairs.
            idempotent int delete_targets(string target, string source)
                throws TargetCtlError;

            // Command telescope to set new target:source for tracking. Start the
            // tracking immediately if `run_tracking` is true.
            idempotent void send_target_to_telescope(string target, string source,
                string telescope, bool run_tracking) throws TargetCtlError;
        };

        //---------------------------------------------------------------------

        // Special constants for computed target's magnitudes (values of 'mag' vector)
        const double MAG_ECLIPSED = 100;   // target is in Earth's shadow
        const double MAG_UNDEFINED = 101;  // magnitude is undefined (e.g. when phase angle = 180 deg)

        dictionary<string, double_seq> fvector_dict;

        struct site_t {
            double latitude;         // [radians]
            double longitude;        // [radians]
            double altitude;         // [radians]
        };

        struct ephem_query_params_t {
            double mjd1;
            double mjd2;
            double step;             // [s]
            double step_separation;  // [radians], not implemented yet, must be 0.0
            double min_elev;         // [radians], limit for elevation above horizon
            site_t site;
            string_seq req_vectors;  // names of requested vectors, e.g. ['mjd', 'ra', 'de'] or empty list [] for all
        };

        struct ephem_chunk_t {
            fvector_dict fvectors;  // ephemeris data as a named sequences of float values
            bool_seq eclipsed;
        };
        sequence<ephem_chunk_t> ephem_chunk_seq;

        struct ephem_data_t {
            string targetspec;
            string ephemsrc;
            ephem_chunk_seq chunks;
        };
        sequence<ephem_data_t> ephem_data_seq;

        interface EphemServ {
            idempotent ephem_data_seq get_ephems(string_seq targetspecs, ephem_query_params_t p);
        };
    };
};


#endif
