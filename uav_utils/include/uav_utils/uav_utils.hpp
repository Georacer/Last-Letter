#include <ros/ros.h>
#include <geometry_msgs/Quaternion.h>
#include <geometry_msgs/Vector3.h>
#include <cstdio>
#include <cmath>
#include <random>

#include "geometry_msgs/Vector3.h"

#include "last_letter_msgs/Geoid.h"

//////////////
// COntrollers
//////////////

class PID
{
	private:
	public:
	///////////
	//Variables
	double P, I, D, satU, satL, Ts, Tau, trim;
	double Iterm, Iprev, Eprev, Uprev, Dprev;
	double output;
	///////////
	//Functions

	//Constructor
	PID (double Pi, double Ii, double Di, double satUi, double satLi, double trim, double Tsi, double Ni);

	//Destructor
	~PID ();

	//Main step
	double step(double error);
	double step(double error, double dt);
	double step(double error, double dt, double derivative);
	void init(void);
};

class APID
{
public:
	///////////
	//Variables
	double P, I, D, satU, satL, Ts, Tau, trim;
	double Pinit, Iinit, Dinit;
	double Iterm, Iprev, Eprev, Uprev, Dprev;
	double Ierror, bumplessI1, bumplessI2, trErr;
	double output;
	///////////
	//Functions

	//Constructor
	APID (double Pi, double Ii, double Di, double satUi, double satLi, double trim, double Tsi, double Ni);

	//Destructor
	~APID ();

	//Main step
	double step(double error, bool track, double trInput);
	void init(void);
};

/////////////////////////////
// WGS84 utility functions //
/////////////////////////////

/**
 * [WGS84_RN Calculate the curvature of the Earth in the prime vertical
 * @param  lat The latitude in degrees
 * @return     RN - radius corresponding to curvature in meters
 */
double WGS84_RN(double lat);

/**
 * [WGS84_RN Calculate the curvature of the Earth in the meridian
 * @param  lat The latitude in degrees
 * @return     RM - radius corresponding to curvature in meters
 */
double WGS84_RM(double lat);


//////////////////////////////
// PPM and PWM functionalities
//////////////////////////////

double PwmToHalfRange(uint16_t pwmValue);
// Convert a 1000-2000 us value to 0-1 range

double PwmToFullValue(uint16_t pwmValue);
// Convert a 1000-2000 us value to -1-1 range

uint16_t HalfRangeToPwm(double signal);
// Convert a 0-1 range to 1000-2000 us range

uint16_t FullRangeToPwm(double signal);
// Convert a -1-1 range to 1000-2000 us range


//////////////////////////
// Miscellaneous Utilities
//////////////////////////

geometry_msgs::Vector3 getAirData (geometry_msgs::Vector3 speeds);
void randomizeUavParameters(ros::NodeHandle n);
void randomizeParameter(ros::NodeHandle n, std::string paramName, double variance);