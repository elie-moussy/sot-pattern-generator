/*+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 * Copyright Projet JRL-Japan, 2007
 *+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 *
 * File:      sotStepComputer.h
 * Project:   SOT
 * Author:    Paul Evrard, Nicolas Mansard
 *
 * Version control
 * ===============
 *
 *  $Id$
 *
 * Description
 * ============
 *
 *
 * ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*/

#ifndef __SOT_SOTSTEPCOMPUTER_FORCE_H__
#define __SOT_SOTSTEPCOMPUTER_FORCE_H__


/* --------------------------------------------------------------------- */
/* --- INCLUDE --------------------------------------------------------- */
/* --------------------------------------------------------------------- */

/* Matrix */
#include <MatrixAbstractLayer/boost.h>
namespace ml = maal::boost;

/* SOT */
#include <dynamic-graph/entity.h>
#include <dynamic-graph/signal-ptr.h>
#include <dynamic-graph/signal-time-dependent.h>
#include <sot-core/matrix-homogeneous.h>
#include <sot-core/vector-roll-pitch-yaw.h>
#include <sot-core/matrix-rotation.h>
#include <sot/sotStepObserver.h>
#include <sot/sotStepChecker.h>
#include <sot/sotStepComputer.h>
/* STD */
#include <string>
#include <deque>
#include <fstream>


/* --------------------------------------------------------------------- */
/* --- API ------------------------------------------------------------- */
/* --------------------------------------------------------------------- */

#if defined (WIN32) 
#  if defined (sotStepComputerForce_EXPORTS) 
#    define SOTSTEPCOMPUTERFORCE_EXPORT __declspec(dllexport)
#  else  
#    define SOTSTEPCOMPUTERFORCE_EXPORT __declspec(dllimport)
#  endif 
#else
#  define SOTSTEPCOMPUTERFORCE_EXPORT
#endif


/* --------------------------------------------------------------------- */
/* --- CLASS ----------------------------------------------------------- */
/* --------------------------------------------------------------------- */

class sotStepQueue;

/// Generates footsteps.
class SOTSTEPCOMPUTERFORCE_EXPORT sotStepComputerForce
  : public dg::Entity, public sotStepComputer
{
 public:

  static const std::string CLASS_NAME;
  virtual const std::string& getClassName( void ) const { return CLASS_NAME; }

 public: // Construction

  sotStepComputerForce( const std::string& name );

 public: // Methods

  void changeFirstStep( sotStepQueue& queue, int timeCurr );
  void nextStep( sotStepQueue& queue, int timeCurr );

 public: // dg::Signals

  dg::SignalPtr< MatrixHomogeneous,int > waistMlhandSIN;
  dg::SignalPtr< MatrixHomogeneous,int > waistMrhandSIN;
  dg::SignalPtr< MatrixHomogeneous,int > referencePositionWaistSIN;
  dg::SignalPtr< ml::Vector,int > stiffnessSIN;
  dg::SignalPtr< ml::Vector,int > velocitySIN;
  dg::SignalPtr< unsigned,int > contactFootSIN;

  dg::SignalTimeDependent< ml::Vector,int > displacementSOUT;
  dg::SignalTimeDependent< ml::Vector,int > forceSOUT;
  dg::SignalTimeDependent< ml::Vector,int > forceLhandSOUT;
  dg::SignalTimeDependent< ml::Vector,int > forceRhandSOUT;

  ml::Vector& computeDisplacement( ml::Vector& res,int timeCurr );
  ml::Vector& computeForce( ml::Vector& res,int timeCurr );
  ml::Vector& computeForceL( ml::Vector& res,int timeCurr );
  ml::Vector& computeForceR( ml::Vector& res,int timeCurr );
  ml::Vector& computeHandForce( ml::Vector& res,
				const MatrixHomogeneous& waMh,
				const MatrixHomogeneous& waMref,
				const ml::Vector& F );

 public: // dg::Entity

  virtual void display( std::ostream& os ) const; 
  virtual void commandLine( const std::string& cmdLine,
			    std::istringstream& cmdArgs,
			    std::ostream& os );

 private: // Reference frame

  MatrixHomogeneous waMref0;
  sotStepObserver* twoHandObserver;
  sotStepChecker checker;

  void thisIsZero();

 private: // Debug

  std::ofstream logChanges;
  std::ofstream logPreview;
};


#endif // #ifndef __SOT_STEPCOMPUTER_H__
