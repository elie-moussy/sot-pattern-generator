/*+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 * Copyright Projet JRL-Japan, 2007
 *+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 *
 * File:      StepComputer.h
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

#ifndef __SOT_StepComputer_FORCE_H__
#define __SOT_StepComputer_FORCE_H__


/* --------------------------------------------------------------------- */
/* --- INCLUDE --------------------------------------------------------- */
/* --------------------------------------------------------------------- */

/* SOT */
#include <dynamic-graph/entity.h>
#include <dynamic-graph/signal-ptr.h>
#include <dynamic-graph/signal-time-dependent.h>
#include <sot/core/matrix-homogeneous.hh>
#include <sot/core/vector-roll-pitch-yaw.hh>
#include <sot/core/matrix-rotation.hh>
#include <sot-pattern-generator/step-observer.h>
#include <sot-pattern-generator/step-checker.h>
#include <sot-pattern-generator/step-computer.h>
/* STD */
#include <string>
#include <deque>
#include <fstream>


/* --------------------------------------------------------------------- */
/* --- API ------------------------------------------------------------- */
/* --------------------------------------------------------------------- */

#if defined (WIN32)
#  if defined (step_computer_force_EXPORTS)
#    define StepComputerFORCE_EXPORT __declspec(dllexport)
#  else
#    define StepComputerFORCE_EXPORT __declspec(dllimport)
#  endif
#else
#  define StepComputerFORCE_EXPORT
#endif

namespace dynamicgraph {
  namespace sot {

    /* --------------------------------------------------------------------- */
    /* --- CLASS ----------------------------------------------------------- */
    /* --------------------------------------------------------------------- */

    class StepQueue;

    /// Generates footsteps.
    class StepComputerFORCE_EXPORT StepComputerForce
      : public Entity, public StepComputer
    {
    public:

      static const std::string CLASS_NAME;
      virtual const std::string& getClassName( void ) const { return CLASS_NAME; }

    public: // Construction

      StepComputerForce( const std::string& name );

    public: // Methods

      void changeFirstStep( StepQueue& queue, int timeCurr );
      void nextStep( StepQueue& queue, int timeCurr );

    public: // Signals

      SignalPtr< MatrixHomogeneous,int > waistMlhandSIN;
      SignalPtr< MatrixHomogeneous,int > waistMrhandSIN;
      SignalPtr< MatrixHomogeneous,int > referencePositionWaistSIN;
      SignalPtr< dynamicgraph::Vector,int > stiffnessSIN;
      SignalPtr< dynamicgraph::Vector,int > velocitySIN;
      SignalPtr< unsigned,int > contactFootSIN;

      SignalTimeDependent< dynamicgraph::Vector,int > displacementSOUT;
      SignalTimeDependent< dynamicgraph::Vector,int > forceSOUT;
      SignalTimeDependent< dynamicgraph::Vector,int > forceLhandSOUT;
      SignalTimeDependent< dynamicgraph::Vector,int > forceRhandSOUT;

      dynamicgraph::Vector& computeDisplacement( dynamicgraph::Vector& res,int timeCurr );
      dynamicgraph::Vector& computeForce( dynamicgraph::Vector& res,int timeCurr );
      dynamicgraph::Vector& computeForceL( dynamicgraph::Vector& res,int timeCurr );
      dynamicgraph::Vector& computeForceR( dynamicgraph::Vector& res,int timeCurr );
      dynamicgraph::Vector& computeHandForce( dynamicgraph::Vector& res,
				    const MatrixHomogeneous& waMh,
				    const MatrixHomogeneous& waMref,
				    const dynamicgraph::Vector& F );

    public: // Entity

      virtual void display( std::ostream& os ) const;
      virtual void commandLine( const std::string& cmdLine,
				std::istringstream& cmdArgs,
				std::ostream& os );

    private: // Reference frame

      MatrixHomogeneous waMref0;
      StepObserver* twoHandObserver;
      StepChecker checker;

      void thisIsZero();

    private: // Debug

      std::ofstream logChanges;
      std::ofstream logPreview;
    };


  } // namespace sot
} // namespace dynamicgraph

#endif // #ifndef __SOT_STEPCOMPUTER_H__

