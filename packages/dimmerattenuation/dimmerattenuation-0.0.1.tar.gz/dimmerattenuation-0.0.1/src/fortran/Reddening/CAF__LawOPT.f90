! ###########################################################################
!     RESUME : CAF = Charlot and Fall (2000), hereafter CAF redenning       !
!              law. Returns:                                                !
!                                                                           !
!              q(λ) = A(λ)/A(V) for given λ in Å.                           !
!                                                                           !
!              q(λ) = ( λ / 5500.0 )**(-m) -> Equation 28/29                !
!                                                                           !
!                                                                           !
!              But it was modified to incorporate R(V). Assuming that       !
!              R(V) = 3.1 is the traditional curve. Therefore,              !
!                                                                           !
!              q(λ) = [ R(V)/3.1 * ( λ / 5500.0 )**(-m) - (R(V)-3.1)/3.1 ]  !
!                                                                           !
!              or                                                           !
!                                                                           !
!              q(λ) = [ R(V)/3.1 * ( λ / 5500.0 )**(-m) - R(V)/3.1 + 1.0 ]  !
!                                                                           !
!              or                                                           !
!                                                                           !
!              q(λ) = R(V) / 3.1 * [ ( λ / 5500.0 )**(-m) - 1.0 ] + 1.0     !
!                                                                           !
!              if R(V) = 3.1, then                                          !
!              q(λ) = 3.1 / 3.1 * [ ( λ / 5500.0 )**(-m) - 1.0 ] + 1.0      !
!              q(λ) = ( λ / 5500.0 )**(-m) - 1.0 + 1.0                      !
!              q(λ) = ( λ / 5500.0 )**(-m)                                  !
!                                                                           !
!     INPUT  : 01) n -> # of elements in l                                  !
!              02) l -> λ                                                   !
!              03) R_V -> is known to be correlated with the average        !
!                         size of the dust grains causing the extinction.   !
!              04) m -> Spectral index for the extinction law               !
!                                                                           !
!     OUTPUT : 01) CAF__LawOPT -> Value of q(λ)                             !
!                                                                           !
!    WARNING : To get the given example behave correctly, one can use       !
!              the following in the corresponding signature for the         !
!              optional variable:                                           !
!              ! f2py real (kind=RP) :: x = 1.0                             !
!                                                                           !
!     PYTHON : Python compatibility using f2py revised. Better usage        !
!              with numpy.                                                  !  
!                                                                           !
!     Written: Jean Michel Gomes © Copyright ®                              !
!        Date: Sun Oct 15 10:00:52 WEST 2006                                !
!     Checked: seg nov 23 16:04:53  WET 2020                                !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE CAF__LawOPT( n,l,q,R_V,m )

    use ModDataType

    implicit none
    real     (kind=RP), optional :: m
    !f2py real (kind=RP) :: m = 0.7
    
    integer  (kind=IB), intent(in) :: n
    real     (kind=RP), intent(in) :: R_V
    real     (kind=RP), intent(in), dimension(0:n-1) :: l
    real     (kind=RP), intent(out), dimension(0:n-1) :: q
    real     (kind=RP) :: index

    !f2py real     (kind=RP), intent(in) :: l
    !f2py                     intent(hide), depend(l) :: n=shape(l,0)

    !f2py real     (kind=RP), intent(out) :: q
    !f2py                     intent(hide), depend(q) :: n=shape(q,0)

    !f2py real     (kind=RP), intent(in) :: R_V

    !f2py real     (kind=RP), optional :: m=0.7
    
    if ( present(m) ) then
       index = m
       !write (*,*) index
    else
       index = 0.7_RP
    end if

    q(0:n-1) = R_V/3.1_RP * (( l(0:n-1) / 5500.0_RP )**(-index) - 1.0_RP) + 1.0_RP

END SUBROUTINE CAF__LawOPT
! ###########################################################################

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE info( a )
  use ModDataType

  implicit none
  
  character (len=CH), intent(out) :: a

  !f2py intent(out) :: a

  a = 'Charlot and Fall (2000) reddening law'
  
END SUBROUTINE info
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE author( a )
  use ModDataType

  implicit none
  
  character (len=CH), intent(out) :: a

  !f2py intent(out) :: a

  a = 'Written by Jean Gomes'
  
END SUBROUTINE author
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
