! ###########################################################################
!     RESUME : Seaton (1979) - old Milky Way law, hereafter S79             !
!              redenning law. Returns:                                      !
!                                                                           !
!              q(λ) = A(λ)/A(V) for given λ in Å. Strictly valid            !
!              between 1000.00 to 10000 Å in the infrared. However,         !
!              changed to extrapolate.                                      !
!                                                                           !
!                                                                           !
!              X(x) = A(λ) / E(B-V), where x = 10000. / λ                   !
!                                                                           !
!              R(V) = A(V) / E(B-V) = > E(B-V) = A(V) / R(V)                !
!                                                                           !
!              X(x) = A(λ) / E(B-V) = A(λ) / A(V) * R(V) = q(λ) * R(V)      !
!                                                                           !
!              q(λ) = X(x) / R(V)                                           !
!                                                                           !
!     INPUT  : 01) n   -> # number of elements in l                         !
!              02) l   -> λ                                                 !
!              03) R_V -> is known to be correlated with the average        !
!                  size of the dust grains causing the extinction.          !
!              04) k -> Variable set to 0 if run aborted                    !
!                                                                           !
!     OUTPUT : 01)  S79__LawOPT -> Value of q(λ)                            !
!                                                                           !
!     PYTHON : Python compatibility using f2py revised. Better usage        !
!              with numpy.                                                  !
!                                                                           !
!     Written: Jean Michel Gomes                                            !
!     Checked: seg nov 23 16:04:53 WET 2020                                 !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE S79__LawOPT( n,l,q,R_V )

    use ModDataType

    integer  (kind=IB) :: i
    real     (kind=RP), intent(in) :: R_V
    real     (kind=RP), intent(in), dimension(0:n-1) :: l
    real     (kind=RP), intent(out), dimension(0:n-1) :: q
    real     (kind=RP), dimension(0:n-1) :: x,k_lambda

    real     (kind=RP), dimension(18) :: xprime,kprime!,b,c,d

    real     (kind=RP) :: e

    !f2py real     (kind=RP), intent(in)  :: l
    !f2py                     intent(hide), depend(l) :: n=shape(l,0)

    !f2py real     (kind=RP), intent(out) :: q
    !f2py                     intent(hide), depend(q) :: n=shape(q,0)

    !f2py real     (kind=RP), intent(in)  :: R_V
    
    interface
       subroutine SPLINE1DArr( x,o,m,t,y,n,e,k )
         use ModDataType
         integer  (kind=IB), intent(in) :: n,m
         integer  (kind=IB), optional :: k
         real     (kind=RP), intent(in), dimension(0:n-1)  :: t,y
         real     (kind=RP), intent(in), dimension(0:m-1)  :: x
         real     (kind=RP), intent(out), dimension(0:m-1) :: o
         real     (kind=RP), optional :: e
       end subroutine SPLINE1DArr
    end interface
    
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!    
    x(0:n-1)        = 10000.0_RP / l(0:n-1)   ! Convert to inverse of microns
    k_lambda(0:n-1) = 0.0_RP
    e               = 1.0e-8_RP
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
! --- Table 3 - Adopted from Nandy et al. (1975) ----------------------------
    kprime = (/ 1.36,1.44,1.84,2.04,2.24,2.44,                              &
                2.66,2.88,3.14,3.36,3.56,3.77,                              &
                3.96,4.15,4.26,4.40,4.52,4.64 /)
    do i=1,18
        ! in IDL findgen(18)*0.1+1.0
        xprime(i) = float(i-1) * 0.1_RP + 1.0_RP
    end do

    do i=0,n-1

       ! Actually valid only from x(i) = 1.0 to 2.7

       if ( x(i) < 2.70_RP ) then
          call SPLINE1DArr( x(i:i),k_lambda(i:i),1,xprime,kprime,18,e,0 )
       end if
       
       ! The following equations are from Table 2 of Seaton (1979)
       ! These are based on X(x) = A(λ) / E(B-V), i.e. k_lambda
       if ( x(i) >= 2.70_RP .AND. x(i) <= 3.65_RP ) then
          k_lambda(i) = 1.56_RP + 1.048_RP * x(i) + 1.01_RP                  &
                      / ((x(i)-4.60_RP)**2+0.280_RP)
       end if
       
       if ( x(i) > 3.65_RP .AND. x(i) <= 7.14_RP ) then
          k_lambda(i) = 2.29_RP+0.848_RP*x(i)+1.01_RP                        &
                      / ((x(i)-4.60_RP)**2+0.280_RP)
       end if
       
       if ( x(i) > 7.14_RP ) then !.AND. x(i) <= 10.0_RP ) then
          k_lambda(i) = 16.17_RP - 3.20_RP*x(i) + 0.2975_RP*x(i)**2
       end if
       
       ! Actually not valid but extrapolated
       !if ( x(i) > 10.0_RP ) then
       !   k_lambda(i) = 16.17_RP - 3.20_RP*x(i) + 0.2975_RP*x(i)**2
       !end if
    end do

    q(0:n-1) = k_lambda(0:n-1) / R_V
       
END SUBROUTINE S79__LawOPT
! ###########################################################################

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE S79__LawOPT_info( a )
  use ModDataType

  implicit none
  
  character (len=31), intent(out) :: a

  !f2py intent(out) :: a
  
  a = 'Seaton (1979) old Milky Way law'
  
END SUBROUTINE S79__LawOPT_info
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE S79__LawOPT_author( a )
  use ModDataType

  implicit none
  
  character (len=21), intent(out) :: a

  !f2py intent(out) :: a
  
  a = 'Written by Jean Gomes'
  
END SUBROUTINE S79__LawOPT_author
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!PROGRAM GeneralProgram
!
!
!END PROGRAM GeneralProgram
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
