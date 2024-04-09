! ###########################################################################
!     RESUME : CCM = Cardelli, Clayton & Mathis  (1989)  redenning  law.    !
!              Returns q(λ) = A(λ)/A(V) for given λ in Å. Strictly valid    !
!              from 1000 to 33333 Å. However, changed to extrapolate.       !
!                                                                           !
!              The equation is given by:                                    !
!                                                                           !
!              *** q(λ) = a(x) + b(x) / R_V                                 !
!                  Where a = a(x) & b = b(x) and x = 1/λ                    !
!                                                                           !
!     INPUT  : 01) m           -> # of elements in array l                  !
!              02) l           -> λ                                         !
!              03) R_V         -> A(V) / E(B-V)                             !
!                                                                           !
!     OUTPUT : 01) Value of q(λ)                                            !
!                                                                           !
!     PYTHON : Python compatibility using f2py revised. Better usage        !
!              with numpy.                                                  !
!                                                                           !
!     Written: Jean Michel Gomes © Copyright ®                              !
!     Checked: seg nov 23 16:04:53 WET 2020                                 !
!     Checked: Mon Dec 20 08:56:10 PM WET 2021                              !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE CCMR_LawOPT( n,l,q,R_V )
    use ModDataType

    implicit none
    integer  (kind=IB), intent(in) :: n
    integer  (kind=IB) :: i

    real     (kind=RP), intent(in), dimension(0:n-1) :: l
    real     (kind=RP), intent(in) :: R_V

    real     (kind=RP), intent(out), dimension(0:n-1) :: q
    real     (kind=RP), dimension(0:n-1) :: x
    
    real     (kind=RP) :: a,b,F_a,F_b,y,z

    !f2py real     (kind=RP), intent(in)  :: l
    !f2py                     intent(hide), depend(l) :: n=shape(l,0)
    
    !f2py real     (kind=RP), intent(out) :: q
    !f2py                     intent(hide), depend(q) :: n=shape(q,0)

    !f2py real     (kind=RP), intent(in)  :: R_V
    
    x(0:n-1) = 10000.0_RP / l(0:n-1)

    do i=0,n-1
    
       a = 00000.0_RP
       b = 00000.0_RP

! *** WARNING ***************************************************************
!    RESUME : Not strictly valid see header of function but extrapolated.   !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       if ( x(i) > 10.0_RP ) then
          z = (x(i) - 8.0_RP)
          a = -1.073_RP - 0.628_RP * z + 0.137_RP * z*z - 0.070_RP * z*z*z
          b = 13.670_RP + 4.257_RP * z - 0.420_RP * z*z + 0.374_RP * z*z*z
       end if
! *** WARNING ***************************************************************

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!     RESUME : Far-Ultraviolet: 8 <= x <= 10 ; 1000 -> 1250 Å.              !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       if ( x(i) >= 8.0_RP .AND. x(i) <= 10.0_RP ) then

          z = (x(i) - 8.0_RP)
          a = -1.073_RP - 0.628_RP * z + 0.137_RP * z*z - 0.070_RP * z*z*z
          b = 13.670_RP + 4.257_RP * z - 0.420_RP * z*z + 0.374_RP * z*z*z

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!     RESUME : Ultraviolet: 3.3 <= x <= 8 ; 1250 -> 3030 Å.                 !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       else if ( x(i) > 3.3_RP .AND. x(i) <= 8.0_RP ) then

          F_a = 0.0_RP
          F_b = 0.0_RP
          if ( x(i) >= 5.9_RP .AND. x(i) <= 8.0_RP ) then
             z   = (x(i) - 5.9_RP)
             F_a = -0.04473_RP * z*z - 0.009779_RP * z*z*z
             F_b = +0.21300_RP * z*z + 0.120700_RP * z*z*z
          end if

          z   = (x(i) - 4.67_RP)
          a =  1.752_RP - 0.316_RP * x(i) - 0.104_RP / (z*z + 0.341_RP) + F_a
          z   = (x(i) - 4.62_RP)
          b = -3.090_RP + 1.825_RP * x(i) + 1.206_RP / (z*z + 0.263_RP) + F_b

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!     RESUME : Optical/NIR: 1.1 <= x <= 3.3 ; 3030 -> 9091 Å.               !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       else if ( x(i) >= 1.1_RP .AND. x(i) <= 3.3_RP ) then

          y = 10000.0_RP / l(i) - 1.82_RP

          a = 1.0_RP+ 0.17699_RP * y - 0.50447_RP * y*y - 0.02427_RP * y*y*y&
            + 0.72085_RP * y*y*y*y + 0.01979_RP * y*y*y*y*y - 0.77530_RP    &
            * y*y*y*y*y*y + 0.32999_RP * y*y*y*y*y*y*y

          b =         1.41338_RP * y + 2.28305_RP * y*y + 1.07233_RP * y*y*y&
            - 5.38434_RP * y*y*y*y - 0.62251_RP * y*y*y*y*y + 5.30260_RP    &
            * y*y*y*y*y*y - 2.09002_RP * y*y*y*y*y*y*y

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!     RESUME : Infrared: 0.3 <= x <= 1.1 ; 9091 -> 33333 Å.                 !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       else if ( x(i) >= 0.3_RP .AND. x(i) < 1.1_RP ) then
          
          a =  0.574_RP * x(i)**1.61_RP
          b = -0.527_RP * x(i)**1.61_RP

       end if

! *** WARNING ***************************************************************
!    RESUME : Not strictly valid see header of function but extrapolated.   !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       if ( x(i) < 0.3_RP ) then
          a =  0.574_RP * x(i)**1.61_RP
          b = -0.527_RP * x(i)**1.61_RP
       end if
! *** WARNING ***************************************************************

       q(i) = a + b / R_V

    end do
       
!    if ( x < 0.3_RP .OR. x > 10.0_RP ) then
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!     RESUME : If λ falls outside 1000 -> 33333 Angs range of CCM89,        !
!              then set q equal to zero.                                    !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!        llow   = 1000.0_RP ; lupp = 33333.0_RP
!        k      = 1_IB
!        i_flag = 0_IB
!    end if
!
!    CCMR_LawOPT = q
    return

END SUBROUTINE CCMR_LAWOPT
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE CCMR_LAWOPT_info( a )
  use ModDataType

  implicit none
  
  character (len=55), intent(out) :: a

  !f2py intent(out) :: a
  
  a = 'Cardelli, Clayton & Mathis  (1989) - CCM extinction law'
  
END SUBROUTINE CCMR_LAWOPT_info
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE CCMR_LAWOPT_author( a )
  use ModDataType

  implicit none
  
  character (len=21), intent(out) :: a

  !f2py intent(out) :: a

  a = 'Written by Jean Gomes'
  
END SUBROUTINE CCMR_LAWOPT_author
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
