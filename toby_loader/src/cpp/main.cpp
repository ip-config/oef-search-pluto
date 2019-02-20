#include <iostream>
#include <stdio.h>
#include <unistd.h>
#include <math.h>

#include "PlaceRepository.h"

using std::cout;
using std::endl;
using std::pair;

using OS = pair<int, int>;

double toRadians(double degrees)
{
  return (degrees * 3.14153) / 180.0;
}

OS toOsGridRef(double lat, double lon)
{
  double φ = toRadians(lat);
  double λ = toRadians(lon);

  double a = 6377563.396, b = 6356256.909;              // Airy 1830 major & minor semi-axes
  double F0 = 0.9996012717;                             // NatGrid scale factor on central meridian
  double φ0 = toRadians(49), λ0 = toRadians(-2);  // NatGrid true origin is 49°N,2°W
  double N0 = -100000;
  double E0 = 400000;                     // northing & easting of true origin, metres
  double e2 = 1 - (b*b)/(a*a);                          // eccentricity squared
  double n = (a-b)/(a+b), n2 = n*n, n3 = n*n*n;         // n, n², n³

  double cosφ = ::cos(φ), sinφ = ::sin(φ);
  double ν = a*F0/::sqrt(1-e2*sinφ*sinφ);            // nu = transverse radius of curvature
  double ρ = a*F0*(1-e2)/::pow(1-e2*sinφ*sinφ, 1.5); // rho = meridional radius of curvature
  double η2 = ν/ρ-1;                                    // eta = ?

  double Ma = (1 + n + (5/4)*n2 + (5/4)*n3) * (φ-φ0);
  double Mb = (3*n + 3*n*n + (21/8)*n3) * ::sin(φ-φ0) * ::cos(φ+φ0);
  double Mc = ((15/8)*n2 + (15/8)*n3) * ::sin(2*(φ-φ0)) * ::cos(2*(φ+φ0));
  double Md = (35/24)*n3 * ::sin(3*(φ-φ0)) * ::cos(3*(φ+φ0));
  double M = b * F0 * (Ma - Mb + Mc - Md);              // meridional arc

  double cos3φ = cosφ*cosφ*cosφ;
  double cos5φ = cos3φ*cosφ*cosφ;
  double tan2φ = ::tan(φ)*::tan(φ);
  double tan4φ = tan2φ*tan2φ;

  double I = M + N0;
  double II = (ν/2)*sinφ*cosφ;
  double III = (ν/24)*sinφ*cos3φ*(5-tan2φ+9*η2);
  double IIIA = (ν/720)*sinφ*cos5φ*(61-58*tan2φ+tan4φ);
  double IV = ν*cosφ;
  double V = (ν/6)*cos3φ*(ν/ρ-tan2φ);
  double VI = (ν/120) * cos5φ * (5 - 18*tan2φ + tan4φ + 14*η2 - 58*tan2φ*η2);

  double Δλ = λ-λ0;
  double Δλ2 = Δλ*Δλ, Δλ3 = Δλ2*Δλ, Δλ4 = Δλ3*Δλ, Δλ5 = Δλ4*Δλ, Δλ6 = Δλ5*Δλ;

  double N = I + II*Δλ2 + III*Δλ4 + IIIA*Δλ6;
  double E = E0 + IV*Δλ + V*Δλ3 + VI*Δλ5;

  return OS(N/1000, E/1000);
}

int main(int argc, char *argv[])
{
  auto pr = PlaceRepository(argv[1]);

  cout << "NAME,LAT,LON,NORTHING_KM,WESTING_KM"<< endl;

  for(auto p : pr.places())
  {
    auto os = toOsGridRef(p.latitude, p.longitude);

    cout
      << p.name << ","
      << p.latitude << ","
      << p.longitude << ","
      << os.first << ","
      << os.second
      << endl;
  }
}
