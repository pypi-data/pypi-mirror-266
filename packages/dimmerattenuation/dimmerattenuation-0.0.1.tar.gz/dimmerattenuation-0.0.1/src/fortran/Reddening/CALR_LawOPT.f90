! ###########################################################################
!     RESUME : CAL = Calzetti et al. (2000) redenning law - Formulas        !
!              in (4) from the article. Returns q(λ) = A(λ)/A(V) for        !
!              given λ in Å. Strictly valid from 1200 to 22000 Å.           !
!              However, it is extrapolated.                                 !
!                                                                           !
!     INPUT  : 01) n   -> # of elements in l                                !
!              02) l   -> λ                                                 !
!              03) R_V -> is known to be correlated with the average        !
!                  size of the dust grains causing the extinction.          !
!                                                                           !
!     OUTPUT : 01) CALR_LawOPT -> Value of q(λ)                             !
!                                                                           !
!     PYTHON : Python compatibility using f2py revised. Better usage        !
!              with numpy.                                                  !  
!                                                                           !
!     Written: Jean Michel Gomes © Copyright ®                              !
!        Date: Sun Oct 15 10:00:52 WEST 2006                                !
!     Checked: seg nov 23 16:04:53  WET 2020                                !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE CALR_LawOPT( n,l,q,R_V )

    use ModDataType

    implicit none
    integer  (kind=IB), intent(in) :: n
    integer  (kind=IB) :: i
    real     (kind=RP), intent(in), dimension(0:n-1) :: l
    real     (kind=RP), intent(out), dimension(0:n-1) :: q
    real     (kind=RP), dimension(0:n-1) :: x
    real     (kind=RP), intent(in) :: R_V

    !f2py real     (kind=RP), intent(in) :: l
    !f2py                     intent(hide), depend(l) :: n=shape(l,0)

    !f2py real     (kind=RP), intent(out) :: q
    !f2py                     intent(hide), depend(q) :: n=shape(q,0)

    !f2py real     (kind=RP), intent(in) :: R_V

    q(0:n-1) = 00000.00_RP
    x(0:n-1) = 10000.00_RP / l
    !R_V = 00004.05_RP

    do i=0,n-1
    
! *** WARNING ***************************************************************
!    RESUME : Not strictly valid see header of function but extrapolated.   !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       if ( l(i) < 1200.0_RP ) then
          q(i) = (2.6590_RP / R_V) * ( -2.1560_RP + 1.5090_RP * x(i)        &
               - 0.19800_RP * x(i)*x(i) + 0.011_RP * x(i)*x(i)*x(i)) + 1.0_RP
       end if
! *** WARNING ***************************************************************

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!     RESUME : UV -> Optical: 1200 -> 6300 Å.                               !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       ! Equation (4) of paper
       if ( l(i) >= 1200.0_RP .AND. l(i) < 6300.0_RP ) then

          q(i) = (2.6590_RP / R_V) * (-2.1560_RP + 1.5090_RP * x(i)         &
               - 0.19800_RP * x(i)*x(i) + 0.011_RP * x(i)*x(i)*x(i)) + 1.0_RP

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!     RESUME : Red -> Infrared.                                             !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       ! Equation (4) of paper
       else if ( l(i) >= 6300.0_RP .AND. l(i) <= 22000.0_RP ) then

          q(i) = (2.659_RP / R_V) * (-1.857_RP + 1.040_RP * x(i)) + 1.0_RP

       end if

! *** WARNING ***************************************************************
!    RESUME : Not strictly valid see header of function but extrapolated.   !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       if ( l(i) > 22000.0_RP ) then
          q(i) = (2.659_RP / R_V) * (-1.857_RP + 1.040_RP * x(i)) + 1.000_RP
       end if
! *** WARNING ***************************************************************

    end do
       
END SUBROUTINE CALR_LawOPT
! ###########################################################################

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE  CALR_LawOPT_info( a )
  use ModDataType

  implicit none
  
  character (len=49), intent(out) :: a

  !f2py intent(out) :: a

  a = 'Calzetti et al. (2000) - Starburst extinction law'
  
END SUBROUTINE CALR_LawOPT_info
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE CALR_LawOPT_author( a )
  use ModDataType

  implicit none
  
  character (len=21), intent(out) :: a

  !f2py intent(out) :: a

  a = 'Written by Jean Gomes'
  
END SUBROUTINE CALR_LawOPT_author
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
