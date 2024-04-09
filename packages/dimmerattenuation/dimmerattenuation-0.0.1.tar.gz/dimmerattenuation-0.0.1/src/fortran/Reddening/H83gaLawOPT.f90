! ###########################################################################
!     RESUME : Howarth (1983) galactic law, hereafter H83 redenning         !
!              law. Returns:                                                !
!                                                                           !
!              q(λ) = A(λ)/A(V) for given λ in Å. Strictly valid from       !
!              1111.111 to 5464.48 Å. However, changed to extrapolate.      !
!                                                                           !
!              X(x) = A(λ) / E(B-V), where x = 10000. / λ                   !
!                                                                           !
!              R(V) = A(V) / E(B-V) = > E(B-V) = A(V) / R(V)                !
!                                                                           !
!              X(x) = A(λ) / E(B-V) = A(λ) / A(V) * R(V) = q(λ) * R(V)      !
!                                                                           !
!              q(λ) = X(x) / R(V)                                           !
!                                                                           !
!              A re-normalization of the curve to R(V) = 3.1 was            !
!              done. For each part, excecpt in the optical, the             !
!              original paper computes a fit using R(V) = 3.1. In the       !
!              infrared (equation 4 of the paper) the normalization of      !
!              q(5500) = 1 was not quite accurate, so it was modified       !
!              from 1.86 to 1.8654772727272728_RP. Also a term R_V -        !
!              3.1 was added in most of the equation, so as to be able      !
!              to compute for distinct R(V)s.                               !
!                                                                           !
!     INPUT  : 01) n   -> # of elements in l                                !
!              02) l   -> λ                                                 !
!              03) R_V -> is known to be correlated with the average        !
!                  size of the dust grains causing the extinction.          !
!                                                                           !
!     OUTPUT : 01) H83gaLawOPT -> Value of q(λ)                             !
!                                                                           !
!     PYTHON : Python compatibility using f2py revised. Better usage        !
!              with numpy.                                                  !
!                                                                           !
!     Written: Jean Michel Gomes © Copyright ®                              !
!     Checked: seg nov 23 16:04:53 WET 2020                                 !
!     Checked: Mon Dec 20 08:56:10 PM WET 2021                              !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE H83gaLawOPT( n,l,q,R_V )
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
    
    x(0:n-1) = 10000.0_RP / l(0:n-1)
    q(0:n-1) = 0.0_RP

    do i=0,n-1

! --- This part comes from Seaton (1979) ------------------------------------      
!     RESUME : There is a re-normalization to R(V) = 3.1 and a factor       !
!              added to take into account different R(V).                   !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

       ! *** Not strictly valid for the far far-UV but...
       if ( x(i) > 10.0_RP ) then !far far UV
          q(i) = R_V - 3.1_RP +((16.07_RP - (3.20_RP * x(i)) + (0.2975*x(i)**2))) ! far far UV
       end if
       
       if ( x(i) > 7.14_RP .AND. x(i) <= 10.0_RP ) then ! far UV
          q(i) = R_V - 3.1_RP + ((16.07_RP - (3.20_RP * x(i)) + (0.2975*x(i)**2))) ! far UV
       end if
       
       if ( x(i) > 3.65_RP .AND. x(i) <= 7.14_RP ) then ! mid UV
          q(i) = R_V - 3.1_RP + ((2.19_RP + (0.848_RP*x(i)) + (1.01_RP/(((x(i)-4.60_RP)**2) + 0.280_RP)))) ! mid UV
       end if
       
       if ( x(i) > 2.75_RP .AND. x(i) <= 3.65_RP ) then ! near UV
          q(i) = R_V - 3.1_RP + ((1.46_RP + (1.048_RP*x(i)) + (1.01_RP/(((x(i)-4.60)**2) + 0.280)))) ! near UV
       end if
! --- This part comes from Seaton (1979) ------------------------------------

! From the paper Equation 1 in the UV: 2.75 <= x <= 9.0 ---------------------
! A good fit to the whole UV region
!if ( x > 2.75_RP ) then
!    q = R_V - 0.236_RP + 0.462_RP*x +0.105_RP*x**2 + 0.454_RP / ((x-4.557_RP)**2+0.293_RP)
!end if
! This equation is for the LMC law ------------------------------------------
       
! *** Optical (Equation 3) **************************************************
       if ( x(i) > 1.83_RP .AND. x(i) <= 2.75_RP ) then
          q(i) = R_V + 2.56_RP*(x(i)-1.83_RP) - 0.993_RP*(x(i)-1.83_RP)**2
       end if
! *** Optical (Equation 3) **************************************************

! *** IR (Equation 4) - A cubic polynomial gives a reasonable fit to the data
       if ( x(i) <= 1.83_RP ) then 
          !q(i) = (( (1.86_RP*x(i)**2) - (0.48_RP*x(i)**3) - (0.1_RP*x(i)))) ! IR (4)
          q(i) = R_V - 3.1_RP + ( ( 1.8654772727272728_RP - 0.48_RP*x(i) )*x(i) - 0.1_RP )*x(i)
       end if
! *** IR (Equation 4) - A cubic polynomial gives a reasonable fit to the data

       if (q(i) < 0.0_RP) then
          q(i) = 0.0_RP
       end if
       
       q(i) = q(i) / R_V
    end do

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!     RESUME : If λ falls outside                                           !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !if ( x <= 1.83_RP .OR. x > 9.0_RP ) then
    !    llow = 10000.0_RP / (9.0_RP) ; lupp = 10000.0_RP / (1.83_RP)
    !    k      = 1_IB
    !    i_flag = 0_IB
    !end if

    return
END SUBROUTINE H83gaLawOPT
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE H83gaLawOPT_info( a )
  use ModDataType

  implicit none
  
  character (len=27), intent(out) :: a

  !f2py intent(out) :: a
  
  a = 'Howarth (1983) galactic law'
  
END SUBROUTINE H83gaLawOPT_info
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE H83gaLawOPT_author( a )
  use ModDataType

  implicit none
  
  character (len=21), intent(out) :: a

  !f2py intent(out) :: a
  
  a = 'Written by Jean Gomes'
  
END SUBROUTINE H83gaLawOPT_author
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
