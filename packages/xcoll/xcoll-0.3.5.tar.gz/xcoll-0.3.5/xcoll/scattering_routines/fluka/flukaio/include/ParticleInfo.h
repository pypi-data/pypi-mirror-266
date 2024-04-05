#ifndef FLUKAIO_PARTICLE_INFO_H__
#define FLUKAIO_PARTICLE_INFO_H__

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Stores particle data as sent through the network 
 * Always using Fluka units
 *
 * Fields:
 *
 * - Particle identification:
 *    - id: Particle id
 *    - gen: Particle generation
 * - Particle info:
 *    - x: Position in x (cm.)
 *    - y: Position in y (cm.)
 *    - z: Position in z (cm.)
 *    - tx: Director cosine in x
 *    - ty: Director cosine in y
 *    - tz: Director cosine in z
 *    - m: Rest mass (GeV/c^2)
 *    - p: Momentum (GeV/c)
 *    - t: Time
 *    - q: Charge
 *    - pdgid: PDG id number
 *    - sx: x component of the particle spin
 *    - sy: y component of the particle spin
 *    - sz: z component of the particle spin
 * - Particle metadata:
 *    - Weight: statistical weight (goes from 0.0 to 1.0)
 *
 */

#pragma pack(1)
typedef struct {
	/* Particle identification */
	uint32_t id;
	uint32_t gen;

	/* Particle attributtes */
	double x;
	double y;
	double z;
	double tx;
	double ty;
	double tz;
	double m;
	double pc;
	double t;

	/* Particle spin */
	double sx;
	double sy;
	double sz;

	int32_t pdgid;

	/* Particle charge */
	int16_t q;

	/* Particle metadata */
	double weight;

} particle_info_t;
#pragma pack()

#ifdef __cplusplus
}
#endif

#endif
