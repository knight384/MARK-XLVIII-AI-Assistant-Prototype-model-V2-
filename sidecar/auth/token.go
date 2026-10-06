package auth

import (
	"fmt"
	"github.com/golang-jwt/jwt/v5"
)

type TokenValidator struct {
	secret []byte
}

func NewTokenValidator(secret string) *TokenValidator {
	return &TokenValidator{
		secret: []byte(secret),
	}
}

func (v *TokenValidator) ValidateToken(tokenStr string) (*jwt.Token, error) {
	token, err := jwt.Parse(tokenStr, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return v.secret, nil
	}, jwt.WithValidMethods([]string{"HS256"}), jwt.WithExpirationRequired())
	
	if err != nil {
		return nil, err
	}
	
	if !token.Valid {
		return nil, fmt.Errorf("invalid token")
	}
	
	return token, nil
}
