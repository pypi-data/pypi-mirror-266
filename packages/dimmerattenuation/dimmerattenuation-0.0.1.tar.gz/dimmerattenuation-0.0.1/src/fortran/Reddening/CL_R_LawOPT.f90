! ###########################################################################
!     RESUME : CL_ = "Calzetti + Leitherer"     - redenning law. Returns    !
!              q(λ) = A(λ)/A(V) for given λ  in Å.                          !
!                                                                           !
!              01) Ultraviolet (UV): switching from Leitherer to Calzetti   !
!                  redenning law at 1846 Å. This is a bit longer than the   !
!                  nominal limit of the Leitherer  law, but it  is  where   !
!                  the two  equations meet & so the transition is smooth.   !
!                                                                           !
!              02) Infra-red (IR): extrapolating the Calzetti law to λ  >   !
!                  22000 Å, q(λ) becomes equal to 0 at 31149.77 Å, thus     !
!                  for λ > 31149 Å.                                         !
!                                                                           !
!     INPUT  : 01) n -> # of elements in l                                  !
!              02) l   -> λ                                                 !
!              03) R_V -> is known to be correlated with the average        !
!                  size of the dust grains causing the extinction.          !
!                                                                           !
!     OUTPUT : 01) CCJR_LawOPT -> Value of q(λ)                             !
!                                                                           !
!     PYTHON : Python compatibility using f2py revised. Better usage        !
!              with numpy.                                                  !
!                                                                           !
!     Written: Jean Michel Gomes © Copyright ®                              !
!        Date: Sun Oct 15 10:00:52 WEST 2006                                !
!     Checked: seg nov 23 16:04:53  WET 2020                                !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE CL_R_LawOPT( n,l,q,R_V )

    use ModDataType

    implicit none
    integer  (kind=IB), intent(in) :: n
    integer  (kind=IB) :: i
    real     (kind=RP), intent(in), dimension(0:n-1) :: l
    real     (kind=RP), intent(out), dimension(0:n-1) :: q
    real     (kind=RP), intent(in) :: R_V
    real     (kind=RP), dimension(0:n-1) :: x

    !f2py real     (kind=RP), intent(in)  :: l
    !f2py                     intent(hide), depend(l) :: n=shape(l,0)

    !f2py real     (kind=RP), intent(out) :: q
    !f2py                     intent(hide), depend(q) :: n=shape(q,0)

    !f2py real     (kind=RP), intent(in)  :: R_V
    
    q(0:n-1) = 00000.00_RP
    x(0:n-1) = 10000.00_RP / l(0:n-1)

    do i=0,n-1
! *** WARNING ***************************************************************
!    RESUME : Not strictly valid see header of function but extrapolated.   !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       if ( l(i) < 912.0_RP ) then
          q(i) = ( 5.4720_RP + 0.6710_RP * x(i) - 9.2180e-3_RP * x(i)*x(i)  &
               + 2.620e-3_RP *  x(i)*x(i)*x(i) ) / R_V * 0.897333002346675
       end if
! *** WARNING ***************************************************************

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!     RESUME : FUV -> 912 -> 1846 Å taken from Leitherer et al. 2002        !
!              (ApJS, 140, 303), equation 14, strictly valid from 970       !
!              to 1800 Å, but extended to 912 -> 1846 Å. Back to normal     !
!                                                                           !
!              OBS: They use E(B_V)_stars in their equation, so we          !
!                   have to divide by R_V, assuming that this value is      !
!                   the same as for the Calzetti redenning law.             !
!                                                                           !
!              OBS: Re-normalize to match Calzetti curve at 1800 Angstroms  !
!                   To get q_leitherer = q_calzetti at 1800                 !
!                   The factor is R_V * 0.897333002346675                   !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!       if ( l(i) >= 912.0_RP .AND. l(i) <= 1846.0_RP ) then
       if ( l(i) >= 912.0_RP .AND. l(i) <= 1800.0_RP ) then
          q(i) = ( 5.4720_RP + 0.6710_RP * x(i) - 9.2180e-3_RP * x(i)*x(i)  &
               + 2.620e-3_RP * x(i)*x(i)*x(i) ) / R_V * 0.897333002346675 

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!     RESUME : UV -> optical: 1846 -> 6300 Å. Calzetti law.                 !
!     RESUME : UV -> optical: 1800 -> 6300 Å. Calzetti law.                 !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!       else if ( l(i) > 1846.0_RP .AND. l(i) <= 6300.0_RP ) then
       else if ( l(i) > 1800.0_RP .AND. l(i) <= 6300.0_RP ) then
          q(i) = (2.659_RP / R_V) * (-2.15600_RP + 1.50900_RP * x(i)        &
               - 0.19800_RP *  x(i)*x(i) + 0.011_RP * x(i)*x(i)*x(i))       &
               + 1.000_RP

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!     RESUME : Red -> Infrared: 6300 -> 31149 Å. Calzetti law,              !
!              originally valid up to 22000 Å, but stretched up to          !
!              31149 Å, where it becomes zero.                              !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       else if ( l(i) > 6300.0_RP .AND. l(i) <= 31149.0_RP ) then

          q(i) = (2.659_RP / R_V) * (-1.857_RP + 1.040_RP * x(i)) + 1.000_RP

       end if

! *** WARNING ***************************************************************
!    RESUME : Not strictly valid see header of function but extrapolated.   !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       if ( l(i) > 31149.0_RP ) then
          q(i) = (2.659_RP / R_V) * (-1.857_RP + 1.040_RP * x(i)) + 1.000_RP
       end if
! *** WARNING ***************************************************************

    end do

END SUBROUTINE CL_R_LawOPT
! ###########################################################################

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE CL_R_LawOPT_info( a )
  use ModDataType

  implicit none
  
  character (len=52), intent(out) :: a

  !f2py intent(out) :: a

  a = 'Calzetti et al. (2000) + Leitherer et al. (2002)'
  
END SUBROUTINE CL_R_LawOPT_info
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE CL_R_LawOPT_author( a )
  use ModDataType

  implicit none
  
  character (len=21), intent(out) :: a

  !f2py intent(out) :: a

  a = 'Written by Jean Gomes'
  
END SUBROUTINE CL_R_LawOPT_author
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
