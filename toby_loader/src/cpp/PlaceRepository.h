//
//  Place.h
//  Nodeography
//
//  Created by Toby Simpson on 18/01/2018.
//  Copyright © 2018 Toby Simpson. All rights reserved.
//

#ifndef Place_h
#define Place_h

#include <string>
#include <vector>

class PlaceRepository final
{
  using string=std::string;
public:
	struct Place
	{
		enum class Type
		{
			Village = 0,
			Town = 1,
			City = 2
		};
		Type		type;
		float		longitude;
		float		latitude;
		std::string	name;
		std::string	county;
		//
		Place()
		{ return; }
		//
		Place& operator = (const Place& rhs)
		{
			type = rhs.type;
			longitude = rhs.longitude;
			latitude = rhs.latitude;
			name = rhs.name;
			county = rhs.county;
			return (*this);
		}	// operator =
	};	// struct Place
	typedef std::vector<Place> VecPlaces;
private:
	VecPlaces		m_Places;
	//
public:
	PlaceRepository(const string &filename);
	~PlaceRepository();
	//
	// Returns a random place:
	const bool GetRandomPlace(Place& out_place);
	//

        const VecPlaces &places() { return m_Places; }

private:
	// Binary data parsing:
	const bool Load(const string &filename);
	const bool ReadString(FILE* fp, std::string& out_string);
};	// class PlaceRepository

#endif /* Place_h */
